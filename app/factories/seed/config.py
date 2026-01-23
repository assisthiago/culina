# api/app/common/seed/seed_config.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

DEFAULT_COUNTS: Dict[str, int] = {
    # Identidade
    "user": 100,
    "account_admin": 20,
    "account_client": 80,
    # Lojas
    "store": 15,
    "opening_hours": 0,  # 0 => auto (7 por store)
    "section": 90,  # total de seções
    "product": 300,  # total de produtos
    "product_section": 450,  # total de relacionamentos through (extras)
    # Endereços
    "address_account": 120,  # endereços "não-default" de accounts
    "address_store": 15,  # endereços "não-default" de stores
    "address_account_default": 100,  # defaults por account (cuidado com o UniqueConstraint)
    "address_store_default": 15,  # defaults por store (cuidado com o UniqueConstraint)
    # Pedidos
    "order": 400,
    "order_item": 1200,  # total de itens (distribuído entre os pedidos)
}


def parse_counts(raw: str) -> Dict[str, int]:
    """
    raw: "user=100,account_client=80,order=400"
    """
    raw = (raw or "").strip()
    if not raw:
        return {}

    out: Dict[str, int] = {}
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    for part in parts:
        if "=" not in part:
            raise ValueError(f"Entrada inválida em --counts: '{part}'. Use key=value, separados por vírgula.")
        k, v = [x.strip() for x in part.split("=", 1)]
        if not v.isdigit():
            raise ValueError(f"Valor inválido em --counts para '{k}': '{v}' não é inteiro.")
        out[k] = int(v)
    return out


def merged_counts(overrides: Dict[str, int]) -> Dict[str, int]:
    c = dict(DEFAULT_COUNTS)
    c.update(overrides or {})
    return c


def validate_counts(counts: Dict[str, int]) -> Tuple[bool, str]:
    """
    Valida chaves básicas e consistência mínima.
    """
    required = [
        "user",
        "account_admin",
        "account_client",
        "store",
        "section",
        "product",
        "order",
        "order_item",
        "address_account_default",
        "address_store_default",
    ]
    for k in required:
        if k not in counts:
            return False, f"Chave obrigatória ausente em counts: '{k}'."

    if counts["store"] <= 0:
        return False, "counts['store'] deve ser > 0."

    if counts["account_admin"] <= 0:
        return False, "counts['account_admin'] deve ser > 0 (stores precisam de owner admin)."

    if counts["order"] > 0 and counts["account_client"] <= 0:
        return False, "Para criar pedidos, counts['account_client'] deve ser > 0."

    # defaults não podem exceder número de owners (senão vai forçar duplicates e falhar)
    # (o comando vai limitar por pool, mas aqui avisamos)
    return True, ""
