from django.utils import timezone
from rest_framework import serializers

from .models import Collect, Payment


class PaymentSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source="donor.get_full_name", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "collect", "donor", "donor_name", "amount", "created_at"]
        read_only_fields = ["donor", "created_at", "collect"]  # <-- Добавили "collect"


class CollectSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    # Вложенный сериализатор для ленты платежей (К5: оптимизация через prefetch)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Collect
        fields = [
            "id",
            "author",
            "author_name",
            "title",
            "occasion",
            "description",
            "target_amount",
            "collected_amount",
            "cover_image",
            "end_date",
            "is_finished",
            "payments",
        ]
        read_only_fields = ["author", "collected_amount"]

    def validate_end_date(self, value):
        """Валидатор: проверка даты завершения (К6)."""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Дата завершения не может быть в прошлом."
            )
        return value
