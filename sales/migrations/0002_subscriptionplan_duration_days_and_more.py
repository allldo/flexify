# Generated by Django 4.2.16 on 2025-05-29 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='duration_days',
            field=models.IntegerField(default=30, help_text='Длительность подписки в днях'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='is_trial',
            field=models.BooleanField(default=False, help_text='Является ли тариф пробным'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='period',
            field=models.CharField(choices=[('trial', 'Пробный период'), ('monthly', 'Месячный'), ('yearly', 'Годовой')], default='monthly', max_length=10),
        ),
    ]
