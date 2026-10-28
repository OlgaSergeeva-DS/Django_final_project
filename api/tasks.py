from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_donation_email_task(amount, collect_title, user_email):
    """Асинхронная задача для отправки письма."""
    send_mail(
        subject="Спасибо за ваше пожертвование!",
        message=f"Вы пожертвовали {amount} на сбор '{collect_title}'. Спасибо!",
        from_email=None,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return f"Письмо отправлено на {user_email}"
