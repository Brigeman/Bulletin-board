import os
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Advertisement
from django.core.mail import send_mail
from celery import shared_task
# from django.contrib.auth.models import User, Advertisement


@shared_task
def send_new_ads_notification():
    # Определение начальной и конечной дат для фильтрации объявлений за последнюю неделю
    end_date = timezone.now()  # Текущая дата и время
    start_date = end_date - timedelta(days=7)  # Дата и время 7 дней назад

    # Фильтрация объявлений за последнюю неделю
    new_ads = Advertisement.objects.filter(created_at__gte=start_date, created_at__lte=end_date)

    # Отправка уведомления об объявлениях, если они есть
    if new_ads.exists():
        # Составляем список адресов электронной почты всех пользователей, которым нужно отправить уведомление
        users_emails = [user.email for user in User.objects.all()]

        # Формируем текст уведомления
        subject = 'Новые объявления за последнюю неделю'
        message = 'Здесь список новых объявлений:\n'
        for ad in new_ads:
            message += f'- {ad.title}\n'

        # Отправляем уведомление по электронной почте каждому пользователю
        send_mail(
            subject,
            message,
            os.getenv('EMAIL_HOST_USER'),  # Адрес отправителя
            users_emails,  # Список адресов получателей
            fail_silently=False,
        )
    else:
        # Если нет новых объявлений, не отправляем уведомление
        pass
