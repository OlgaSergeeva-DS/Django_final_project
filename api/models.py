import os

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# Create your models here.
class Collect(models.Model):
    """Модель группового денежного сбора (К3)."""

    OCCASION_CHOICES = [
        ("birthday", "День рождения"),
        ("wedding", "Свадьба"),
        ("charity", "Благотворительность"),
        ("other", "Другое"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name="Автор сбора",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    occasion = models.CharField(
        max_length=20, choices=OCCASION_CHOICES, verbose_name="Повод"
    )
    description = models.TextField(verbose_name="Описание")
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Целевая сумма",
        help_text="Оставьте пустым для бесконечного сбора",
        validators=[MinValueValidator(0)],
    )
    collected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Собранная сумма",
        validators=[MinValueValidator(0)],
    )
    cover_image = models.ImageField(
        upload_to="covers/", null=True, blank=True, verbose_name="Обложка"
    )
    end_date = models.DateTimeField(verbose_name="Дата и время завершения")

    class Meta:
        verbose_name = "Групповой сбор"
        verbose_name_plural = "Групповые сборы"
        ordering = ["-end_date"]

    def __str__(self):
        return f"{self.title} ({self.author})"

    @property
    def is_finished(self):
        return timezone.now() > self.end_date

    def delete(self, *args, **kwargs):
        """Удаляем файл обложки с диска при удалении сбора (К4)."""
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)
        super().delete(*args, **kwargs)


class Payment(models.Model):
    """Модель платежа (пожертвования) для сбора (К2)."""

    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Сбор",
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
        verbose_name="Донатер",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма",
        validators=[MinValueValidator(0.01)],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.donor} -> {self.collect}: {self.amount}"
