# api/app/common/management/commands/seed_db.py

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Set

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction

from app.account.models import Account, Address
from app.factories.account import AccountFactory
from app.factories.address import AddressFactory
from app.factories.opening_hours import OpeningHoursFactory
from app.factories.order import OrderFactory
from app.factories.product import ProductFactory
from app.factories.product_sections import ProductSectionFactory
from app.factories.section import SectionFactory
from app.factories.seed.config import merged_counts, parse_counts, validate_counts
from app.factories.store import StoreFactory

# Factories (ajuste os imports se seus paths forem diferentes)
from app.factories.user import UserFactory
from app.order.models import Order, OrderItem
from app.product.models import Product, ProductSections, Section
from app.store.models import OpeningHours, Store


@dataclass
class Pools:
    users: List[Any]
    accounts_admin: List[Any]
    accounts_client: List[Any]
    stores: List[Any]
    sections_by_store_id: Dict[int, List[Any]]
    products_by_store_id: Dict[int, List[Any]]
    account_addresses_by_account_id: Dict[int, List[Any]]
    store_addresses_by_store_id: Dict[int, List[Any]]
    orders: List[Any]


class Command(BaseCommand):
    help = "Popula o banco com dados realistas (PT-BR), respeitando constraints e relações."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--using", type=str, default="default", help="Alias do database em DATABASES (default).")
        parser.add_argument(
            "--counts",
            type=str,
            default="",
            help=(
                "Contagens por chave. Ex.: "
                '"user=100,account_admin=20,account_client=80,store=15,section=90,product=300,order=400,order_item=1200"'
            ),
        )
        parser.add_argument("--dry-run", action="store_true", help="Executa e faz rollback no final.")
        parser.add_argument(
            "--truncate", action="store_true", help="ATENÇÃO: TRUNCATE em todas as tabelas managed antes do seed."
        )
        parser.add_argument(
            "--seed", type=int, default=0, help="Seed do random para reprodutibilidade (0 = aleatório)."
        )
        parser.add_argument("--verbosity-steps", action="store_true", help="Log detalhado por etapa (mais verboso).")

    def handle(self, *args: Any, **options: Any) -> None:
        using: str = options["using"]
        dry_run: bool = bool(options["dry_run"])
        truncate: bool = bool(options["truncate"])
        seed_value: int = int(options["seed"] or 0)
        verbose_steps: bool = bool(options["verbosity_steps"])

        self._ensure_connection(using)

        # Parse counts
        try:
            overrides = parse_counts(options.get("counts", ""))
        except ValueError as e:
            raise CommandError(str(e)) from e

        counts = merged_counts(overrides)

        ok, msg = validate_counts(counts)
        if not ok:
            raise CommandError(msg)

        # Random seed
        rng = random.Random(seed_value if seed_value != 0 else None)

        self.stdout.write(
            self.style.MIGRATE_HEADING(f"[seed_db] using={using} counts={counts} seed={seed_value or 'random'}")
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("[seed_db] DRY-RUN: rollback ao final."))
        if truncate:
            self.stdout.write(self.style.WARNING("[seed_db] TRUNCATE habilitado: limpando tabelas managed (dev only)."))

        try:
            with transaction.atomic(using=using):
                if truncate:
                    self._truncate_all(using)

                pools = self._run_seed(using=using, counts=counts, rng=rng, verbose=verbose_steps)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[seed_db] OK. users={len(pools.users)} "
                        f"accounts_admin={len(pools.accounts_admin)} accounts_client={len(pools.accounts_client)} "
                        f"stores={len(pools.stores)} orders={len(pools.orders)}"
                    )
                )

                if dry_run:
                    raise _ForceRollback()

        except _ForceRollback:
            self.stdout.write(self.style.WARNING("[seed_db] DRY-RUN finalizado com rollback."))
            return

    # -------------------------
    # Seed orchestration
    # -------------------------

    def _run_seed(self, using: str, counts: Dict[str, int], rng: random.Random, verbose: bool) -> Pools:
        # 1) Users (opcional: você pode usar Users diretamente ou deixar Accounts criar via SubFactory)
        # Aqui criamos users para "volume" e realismo, mas Accounts também criam users próprios.
        users = UserFactory.create_batch(counts["user"])
        self._log(verbose, f"users: {len(users)}")

        # 2) Accounts (separados por tipo)
        accounts_admin = AccountFactory.create_batch(counts["account_admin"], type=Account.TYPE_ADMIN)
        accounts_client = AccountFactory.create_batch(counts["account_client"], type=Account.TYPE_CLIENT)
        self._log(verbose, f"accounts_admin: {len(accounts_admin)} | accounts_client: {len(accounts_client)}")

        # 3) Stores (owner admin)
        stores: List[Store] = []
        for _ in range(counts["store"]):
            owner = rng.choice(accounts_admin)
            stores.append(StoreFactory.create(owner=owner))
        self._log(verbose, f"stores: {len(stores)}")

        # 4) OpeningHours
        opening_hours_target = counts.get("opening_hours", 0)
        if opening_hours_target <= 0:
            # auto: 7 por store
            for s in stores:
                for weekday in range(1, 8):
                    # garante unique (store, weekday)
                    OpeningHoursFactory.create(store=s, weekday=weekday)
            self._log(verbose, f"opening_hours: {len(stores) * 7} (auto)")
        else:
            # Cria até o target, distribuindo por store e weekday sem repetir
            created = 0
            for s in stores:
                for weekday in range(1, 8):
                    if created >= opening_hours_target:
                        break
                    OpeningHoursFactory.create(store=s, weekday=weekday)
                    created += 1
                if created >= opening_hours_target:
                    break
            self._log(verbose, f"opening_hours: {created} (custom)")

        # 5) Sections (distribuir por store)
        sections_by_store_id: Dict[int, List[Section]] = {s.id: [] for s in stores}
        for _ in range(counts["section"]):
            s = rng.choice(stores)
            sec = SectionFactory.create(store=s)
            sections_by_store_id[s.id].append(sec)

        # Garantia mínima: cada store deve ter ao menos 1 section, para não quebrar Product
        for s in stores:
            if not sections_by_store_id[s.id]:
                sec = SectionFactory.create(store=s)
                sections_by_store_id[s.id].append(sec)

        self._log(verbose, f"sections: {sum(len(v) for v in sections_by_store_id.values())}")

        # 6) Products (garantir Product.store == Product.section.store)
        products_by_store_id: Dict[int, List[Product]] = {s.id: [] for s in stores}
        for _ in range(counts["product"]):
            s = rng.choice(stores)
            sec_pool = sections_by_store_id[s.id]
            sec = rng.choice(sec_pool)
            p = ProductFactory.create(store=s, section=sec)
            products_by_store_id[s.id].append(p)

        # Garantia mínima: cada store deve ter ao menos 1 product, para orders/items realistas
        for s in stores:
            if not products_by_store_id[s.id]:
                sec = rng.choice(sections_by_store_id[s.id])
                p = ProductFactory.create(store=s, section=sec)
                products_by_store_id[s.id].append(p)

        self._log(verbose, f"products: {sum(len(v) for v in products_by_store_id.values())}")

        # 7) ProductSections (through) - extras M2M
        product_sections_total = counts.get("product_section", 0)
        if product_sections_total > 0:
            created = 0
            # flatten products
            all_products: List[Product] = [p for plist in products_by_store_id.values() for p in plist]
            while created < product_sections_total:
                prod = rng.choice(all_products)
                sec_pool = sections_by_store_id.get(prod.store_id) or []
                if not sec_pool:
                    break

                # escolher uma section da mesma store; evitar repetição óbvia com a primary section
                sec = rng.choice(sec_pool)
                if sec.id == prod.section_id and len(sec_pool) > 1:
                    sec = rng.choice([x for x in sec_pool if x.id != prod.section_id])

                # create through
                ProductSectionFactory.create(product=prod, section=sec, position=created)
                created += 1

            self._log(verbose, f"product_sections (through): {created}")

        # 8) Addresses (XOR) + defaults
        account_addresses_by_account_id: Dict[int, List[Address]] = {
            a.id: [] for a in (accounts_admin + accounts_client)
        }
        store_addresses_by_store_id: Dict[int, List[Address]] = {s.id: [] for s in stores}

        # Defaults por account (respeitando UniqueConstraint)
        default_acc_target = min(counts.get("address_account_default", 0), len(account_addresses_by_account_id))
        if default_acc_target > 0:
            owners = list(account_addresses_by_account_id.keys())
            rng.shuffle(owners)
            for acc_id in owners[:default_acc_target]:
                acc = self._find_by_id(accounts_admin + accounts_client, acc_id)
                addr = AddressFactory.create(account=acc, store=None, is_default=True, label="Casa")
                account_addresses_by_account_id[acc_id].append(addr)
            self._log(verbose, f"address_account_default: {default_acc_target}")

        # Defaults por store
        default_store_target = min(counts.get("address_store_default", 0), len(store_addresses_by_store_id))
        if default_store_target > 0:
            owners = list(store_addresses_by_store_id.keys())
            rng.shuffle(owners)
            for store_id in owners[:default_store_target]:
                st = self._find_by_id(stores, store_id)
                addr = AddressFactory.create(account=None, store=st, is_default=True, label="Matriz")
                store_addresses_by_store_id[store_id].append(addr)
            self._log(verbose, f"address_store_default: {default_store_target}")

        # Addresses extras (não-default) para accounts
        for _ in range(max(0, counts.get("address_account", 0))):
            acc = rng.choice(accounts_admin + accounts_client)
            addr = AddressFactory.create(account=acc, store=None, is_default=False)
            account_addresses_by_account_id[acc.id].append(addr)
        self._log(verbose, f"address_account (extras): {counts.get('address_account', 0)}")

        # Addresses extras (não-default) para stores
        for _ in range(max(0, counts.get("address_store", 0))):
            st = rng.choice(stores)
            addr = AddressFactory.create(account=None, store=st, is_default=False)
            store_addresses_by_store_id[st.id].append(addr)
        self._log(verbose, f"address_store (extras): {counts.get('address_store', 0)}")

        # 9) Orders
        orders: List[Order] = []
        for _ in range(counts["order"]):
            st = rng.choice(stores)
            acc = rng.choice(accounts_client)

            # para realismo, usar endereço do cliente se existir
            addr = self._pick_prefer_default(account_addresses_by_account_id.get(acc.id, []), rng=rng)

            if addr:
                o = OrderFactory.create(
                    store=st,
                    account=acc,
                    zip_code=addr.zip_code,
                    street=addr.street,
                    number=addr.number,
                    neighborhood=addr.neighborhood,
                    complement=addr.complement,
                    reference=addr.reference,
                    city=addr.city,
                    state=addr.state,
                    latitude=addr.latitude,
                    longitude=addr.longitude,
                )
            else:
                o = OrderFactory.create(store=st, account=acc)

            orders.append(o)

        self._log(verbose, f"orders: {len(orders)}")

        # 10) OrderItems total distribuído entre orders
        total_items = max(0, counts.get("order_item", 0))
        if orders and total_items > 0:
            self._create_order_items_distributed(
                orders=orders,
                products_by_store_id=products_by_store_id,
                total_items=total_items,
                rng=rng,
                verbose=verbose,
            )

        return Pools(
            users=users,
            accounts_admin=accounts_admin,
            accounts_client=accounts_client,
            stores=stores,
            sections_by_store_id=sections_by_store_id,
            products_by_store_id=products_by_store_id,
            account_addresses_by_account_id=account_addresses_by_account_id,
            store_addresses_by_store_id=store_addresses_by_store_id,
            orders=orders,
        )

    # -------------------------
    # OrderItems logic
    # -------------------------

    def _create_order_items_distributed(
        self,
        orders: List[Order],
        products_by_store_id: Dict[int, List[Product]],
        total_items: int,
        rng: random.Random,
        verbose: bool,
    ) -> None:
        """
        Distribui `total_items` entre `orders`, garantindo:
        - itens usam produtos da mesma store do order
        - unique(order, product_uuid)
        - recalcula totals no final de cada order
        """
        # Distribuição base: itens por pedido ~ total_items / len(orders)
        n_orders = len(orders)
        base = total_items // n_orders
        remainder = total_items % n_orders

        created_total = 0
        for i, order in enumerate(orders):
            target = base + (1 if i < remainder else 0)
            if target <= 0:
                continue

            prod_pool = products_by_store_id.get(order.store_id) or []
            if not prod_pool:
                continue

            # para garantir unique(product_uuid) por order, usamos sample sem repetição
            # target não pode exceder o tamanho do pool
            target = min(target, len(prod_pool))
            chosen_products = rng.sample(prod_pool, k=target) if target > 1 else [rng.choice(prod_pool)]

            for prod in chosen_products:
                # aplica desconto simples (opcional)
                unit_price = prod.price
                try:
                    if prod.discount_percentage and Decimal(prod.discount_percentage) > 0:
                        discount = Decimal(prod.discount_percentage) / Decimal("100.00")
                        unit_price = (Decimal(prod.price) * (Decimal("1.00") - discount)).quantize(Decimal("0.01"))
                except Exception:
                    unit_price = prod.price

                qty = rng.randint(1, 3)

                OrderItem.objects.create(
                    order=order,
                    product_uuid=prod.uuid,
                    product_name=prod.name,
                    unit_price=unit_price,
                    quantity=qty,
                )
                created_total += 1

            # recalcula e salva totals
            order.recalculate_totals()
            order.save(update_fields=["subtotal", "total"])

        self._log(verbose, f"order_items: {created_total} (distribuídos)")

    # -------------------------
    # Utilities
    # -------------------------

    def _ensure_connection(self, using: str) -> None:
        connections[using].ensure_connection()

    def _truncate_all(self, using: str) -> None:
        tables: List[str] = []
        for m in apps.get_models():
            if m._meta.managed:
                tables.append(m._meta.db_table)
        tables = sorted(set(tables))
        if not tables:
            return
        sql = "TRUNCATE TABLE " + ", ".join(f'"{t}"' for t in tables) + " RESTART IDENTITY CASCADE;"
        with connections[using].cursor() as cursor:
            cursor.execute(sql)

    def _log(self, enabled: bool, msg: str) -> None:
        if enabled:
            self.stdout.write(self.style.HTTP_INFO(f"[seed_db] {msg}"))

    def _find_by_id(self, items: Sequence[Any], pk: int) -> Any:
        for x in items:
            if getattr(x, "id", None) == pk:
                return x
        raise CommandError(f"[seed_db] item id={pk} não encontrado no pool.")

    def _pick_prefer_default(self, addresses: List[Address], rng: random.Random) -> Optional[Address]:
        if not addresses:
            return None
        defaults = [a for a in addresses if getattr(a, "is_default", False)]
        if defaults:
            return rng.choice(defaults)
        return rng.choice(addresses)


class _ForceRollback(Exception):
    pass
