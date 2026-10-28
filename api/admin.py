from django.contrib import admin

from .models import Collect, Payment


# Register your models here.
@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "occasion",
        "target_amount",  # <-- Добавили целевую сумму
        "collected_amount",  # <-- Собранная сумма (уже была)
        "end_date",
    )
    list_filter = ("occasion", "end_date")
    search_fields = ("title", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("collect", "donor", "amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("collect__title", "donor__username")
