from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from app.account.inlines import AddressInline
from app.account.models import Account, Address
from app.utils import BaseAdmin

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Changelist
    list_display = (
        "see_more",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    search_help_text = "Buscar por nome de usuário, nome, sobrenome ou e-mail"

    @display(description="")
    def see_more(self, obj):
        return mark_safe('<span class="material-symbols-outlined">visibility</span>')


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# Admins
@admin.register(Account)
class AccountAdmin(BaseAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    # Changelist
    list_display = (
        "see_more",
        "id",
        "user_full_name",
        "user_email",
        "user_type",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "cpf",
        "phone",
    )
    search_help_text = "Buscar por nome, e-mail, cpf ou telefone"
    list_filter = BaseAdmin.list_filter + ("type",)

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "user",
                    "type",
                    "cpf",
                    "phone",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    inlines = [AddressInline]
    autocomplete_fields = ("user",)

    # Display functions
    @display(description="Nome")
    def user_full_name(self, obj):
        return obj.user.get_full_name()

    @display(description="E-mail")
    def user_email(self, obj):
        return obj.user.email

    @display(
        description="Tipo",
        label={
            Account.TYPE_CLIENT: "primary",
            Account.TYPE_ADMIN: "success",
        },
    )
    def user_type(self, obj):
        return obj.type, obj.get_type_display()

    # Actions


@admin.register(Address)
class AddressAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "account",
                "account__user",
                "store",
            )
        )

    # Changelist
    list_display = (
        "see_more",
        "id",
        "get_account_or_store",
        "get_formatted_zip_code",
        "get_type_of",
        "is_default",
    )
    search_fields = ()
    search_help_text = "Buscar por nome, e-mail, cpf ou telefone"
    list_filter = BaseAdmin.list_filter

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "account",
                    "store",
                    "label",
                    "is_default",
                    "zip_code",
                    "street",
                    "number",
                    "neighborhood",
                    "city",
                    "state",
                    "complement",
                ),
            },
        ),
        (
            "Geolocalização",
            {
                "classes": ("tab",),
                "fields": (
                    "latitude",
                    "longitude",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    autocomplete_fields = ("account", "store")
    readonly_fields = BaseAdmin.readonly_fields + ("latitude", "longitude")

    # Display functions
    @display(description="Nome")
    def get_account_or_store(self, obj):
        if obj.account:
            return obj.account.user.get_full_name()
        elif obj.store:
            return obj.store.name

    @display(
        description="Tipo",
        label={
            "store": "warning",
            Account.TYPE_CLIENT: "success",
            Account.TYPE_ADMIN: "info",
        },
    )
    def get_type_of(self, obj):
        if obj.store:
            return "store", "Loja"
        if obj.account.type == Account.TYPE_CLIENT:
            return Account.TYPE_CLIENT, "Cliente"
        else:
            return Account.TYPE_ADMIN, "Administrador"

    @display(description="CEP")
    def get_formatted_zip_code(self, obj):
        return obj.format_zip_code()

    # Actions
