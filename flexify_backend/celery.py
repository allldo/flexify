
import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexify_backend.settings')

app = Celery('flexify_backend')

# Использование настроек Django для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач в приложениях
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'sales.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Выполнять ежедневно в полночь
    },
}