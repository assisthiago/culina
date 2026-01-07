from rest_framework import serializers

from app.store.models import OpeningHours, Store
from app.utils import BaseSerializer


class OpeningHoursSerializer(BaseSerializer):

    weekday = serializers.CharField(source="get_weekday_display")
    from_hour = serializers.TimeField(format="%H:%M")
    to_hour = serializers.TimeField(format="%H:%M")

    def get_weekday_display(self, obj):
        return obj.get_weekday_display()

    class Meta:
        model = OpeningHours
        exclude = (
            "id",
            "store",
        )


class StoreSerializer(BaseSerializer):

    # Nested serializers
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)

    # Fields
    cnpj = serializers.SerializerMethodField(method_name="cnpj_formatted")

    def cnpj_formatted(self, obj):
        return obj.cnpj_formatted()

    class Meta:
        model = Store
        exclude = BaseSerializer.Meta.exclude + ("owner",)
