import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Collect, Payment


class Command(BaseCommand):
    help = "Генерирует моковые данные: пользователей, сборы и платежи"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаем генерацию данных...")

        # 1. Создаем тестовых пользователей
        users = []
        for i in range(10):
            username = f"user_{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            if created:
                user.set_password("password123")
                user.save()
            users.append(user)

        self.stdout.write(f"Создано/проверено {len(users)} пользователей.")

        # 2. Создаем сборы
        occasions = ["birthday", "wedding", "charity", "other"]
        collects = []

        # Создаем 2000 сборов
        for i in range(2000):
            # Случайная дата завершения (от 1 дня назад до 30 дней вперед)
            end_date = timezone.now() + timedelta(days=random.randint(-1, 30))

            collect = Collect(
                author=random.choice(users),
                title=f"Сбор на {random.choice(['отпуск', 'машину', 'ремонт', 'книги', 'концерт'])} №{i}",
                occasion=random.choice(occasions),
                description=f"Это тестовое описание для сбора №{i}. Помогите кто чем может!",
                target_amount=(
                    Decimal(random.randint(1000, 100000))
                    if random.random() > 0.1
                    else None
                ),
                end_date=end_date,
            )
            collects.append(collect)

        # Используем bulk_create для быстрой вставки в базу (это оптимизация!)
        Collect.objects.bulk_create(collects)
        self.stdout.write(f"Создано {len(collects)} сборов.")

        # 3. Создаем платежи (по 5-15 платежей на каждый сбор)
        all_collects = list(Collect.objects.all())
        payments = []

        for collect in all_collects:
            # Пропускаем, если сбор уже завершен
            if collect.end_date < timezone.now():
                continue

            num_payments = random.randint(5, 15)
            for _ in range(num_payments):
                payment = Payment(
                    collect=collect,
                    donor=random.choice(users),
                    amount=Decimal(random.randint(100, 5000)),
                )
                payments.append(payment)

        Payment.objects.bulk_create(payments)
        self.stdout.write(f"Создано {len(payments)} платежей.")

        self.stdout.write(self.style.SUCCESS("Генерация данных успешно завершена!"))
