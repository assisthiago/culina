from unfold.admin import TabularInline

from app.account.models import Address


class AddressInline(TabularInline):

    model = Address
    tab = True
    extra = 0
    fields = (
        "zip_code",
        "street",
        "number",
        "complement",
        "neighborhood",
        "city",
        "state",
        "is_default",
    )
    readonly_fields = (
        "account",
        "store",
    )
