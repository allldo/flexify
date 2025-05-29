# sales/tasks.py
from celery import shared_task
from django.utils import timezone

from cabinet.models import Profile
from constructor.models import CustomSite


@shared_task
def check_expired_subscriptions():
    """
    Периодическая задача для проверки истекших подписок
    и отключения сайтов пользователей с истекшими подписками
    """
    today = timezone.now().date()

    # Находим все профили с истекшими подписками
    expired_profiles = Profile.objects.filter(
        subscription_end_date__lt=today,
        is_active=True
    )

    # Обновляем статус активности подписки
    count = 0
    for profile in expired_profiles:
        profile.is_active = False
        profile.save()

        # Отключаем (снимаем с публикации) все сайты пользователя
        site_count = CustomSite.objects.filter(user=profile.user).update(is_published=False)
        count += 1

    return f"Проверено {count} истекших подписок"


def create_default_trial_subscription(user):
    """
    Создает пробную подписку для нового пользователя
    """
    from sales.models import SubscriptionPlan
    from cabinet.models import Profile

    # Находим пробный тарифный план
    trial_plan = SubscriptionPlan.objects.filter(is_trial=True).first()

    if trial_plan:
        # Создаем или обновляем профиль пользователя
        profile, created = Profile.objects.get_or_create(user=user)
        profile.subscription_plan = trial_plan
        profile.subscription_start_date = timezone.now().date()
        profile.is_active = True
        profile.save()  # save() автоматически рассчитает subscription_end_date

        return profile

    return None