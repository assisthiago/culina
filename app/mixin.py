from django.core.exceptions import ImproperlyConfigured


class OwnerScopeAdminMixin:
    """
    Scope do Django Admin para mostrar apenas dados das Stores pertencentes ao owner logado.

    Requer:
      - request.user.account (OneToOne com User)
      - Store.owner = ForeignKey(Account, related_name="stores")
    """

    scope_field: str | None = None  # ex: "store", "order__store", "pk"

    def is_super(self, request) -> bool:
        return request.user.is_superuser

    def get_owner_account(self, request):
        return getattr(request.user, "account", None)

    def get_owner_stores_qs(self, request):
        account = self.get_owner_account(request)
        if not account:
            return None
        return account.stores.all()

    def get_scope_filter(self, request):
        if self.is_super(request):
            return None

        if self.scope_field is None:
            raise ImproperlyConfigured("OwnerScopeAdminMixin requires 'scope_field' to be set.")

        stores_qs = self.get_owner_stores_qs(request)
        if stores_qs is None:
            return {"pk__in": []}

        # Caso especial: o próprio model é Store (filtra por pk IN stores)
        if self.scope_field == "pk":
            return {"pk__in": stores_qs.values_list("pk", flat=True)}

        # Normal: o model tem FK (direta ou indireta) para Store
        return {f"{self.scope_field}__in": stores_qs}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        scope = self.get_scope_filter(request)
        return qs if scope is None else qs.filter(**scope)
