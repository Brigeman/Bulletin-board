import os
from celery import Celery

# Устанавливаем переменную окружения, чтобы Celery знал, какую конфигурацию Django использовать.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Создаем экземпляр Celery
app = Celery('project')

# Загружаем конфигурацию Celery из модуля Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи из приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
