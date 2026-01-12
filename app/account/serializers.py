from django.contrib.auth.models import User
from rest_framework import serializers

from app.account.models import Account, Address
from app.utils import BaseSerializer


class AddressSerializer(BaseSerializer):

    zip_code = serializers.SerializerMethodField(method_name="get_formatted_zip_code")

    class Meta:
        model = Address
        exclude = BaseSerializer.Meta.exclude + (
            "account",
            "store",
        )
        ordering = ["-created_at", "is_default"]

    def get_formatted_zip_code(self, obj):
        return obj.format_zip_code()


class UserSerializer(BaseSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )


class AccountSerializer(BaseSerializer):

    # Nested representations
    user = UserSerializer(many=False, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    # Fields
    cpf = serializers.SerializerMethodField(method_name="get_formatted_cpf")
    phone = serializers.SerializerMethodField(method_name="get_formatted_phone")

    class Meta:
        model = Account
        exclude = BaseSerializer.Meta.exclude
        ordering = ["-created_at"]

    def get_formatted_cpf(self, obj):
        return obj.format_cpf()

    def get_formatted_phone(self, obj):
        return obj.format_phone()
