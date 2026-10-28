from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Collect, Payment


class CollectApiTests(TestCase):
    """Тесты для проверки работы API сборов (К7)."""

    def setUp(self):
        """Создаем тестовые данные перед каждым тестом."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="test@example.com"
        )
        # URL-адреса для тестов
        self.collect_list_url = reverse("collect-list")

        # Данные для создания сбора
        self.valid_collect_data = {
            "title": "Тестовый сбор",
            "occasion": "birthday",
            "description": "Описание тестового сбора",
            "target_amount": "10000.00",
            "end_date": (timezone.now() + timedelta(days=5)).isoformat(),
        }

    def test_create_collect_authenticated(self):
        """Авторизованный пользователь может создать сбор."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.collect_list_url, self.valid_collect_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collect.objects.count(), 1)
        self.assertEqual(Collect.objects.first().title, "Тестовый сбор")

    def test_create_collect_unauthenticated(self):
        """Неавторизованный пользователь не может создать сбор."""
        response = self.client.post(
            self.collect_list_url, self.valid_collect_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_collect_with_past_date_fails(self):
        """Валидатор не должен пропускать сбор с датой в прошлом (К6)."""
        self.client.force_authenticate(user=self.user)

        invalid_data = self.valid_collect_data.copy()
        invalid_data["end_date"] = (timezone.now() - timedelta(days=1)).isoformat()

        response = self.client.post(self.collect_list_url, invalid_data, format="json")

        # Ожидаем ошибку 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем, что ошибка именно про дату
        self.assertIn("end_date", response.data)

    def test_make_donation(self):
        """Пользователь может сделать пожертвование в сбор."""
        self.client.force_authenticate(user=self.user)

        # 1. Сначала создаем сбор
        collect = Collect.objects.create(
            author=self.user,
            title="Сбор для доната",
            occasion="charity",
            description="Помогите",
            end_date=timezone.now() + timedelta(days=10),
        )

        # 2. Делаем пожертвование
        donate_url = reverse("collect-donate", args=[collect.id])
        response = self.client.post(donate_url, {"amount": "500.00"}, format="json")

        # 3. Проверяем
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

        # Проверяем, что сумма в сборе обновилась
        collect.refresh_from_db()
        self.assertEqual(collect.collected_amount, 500)
