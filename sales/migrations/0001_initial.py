# Generated by Django 4.2.16 on 2024-12-11 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('constructor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True)),
                ('max_sites', models.PositiveIntegerField(default=1, verbose_name='Максимальное количество сайтов')),
                ('allowed_blocks', models.ManyToManyField(related_name='available_in_plans', to='constructor.blocktype')),
            ],
        ),
    ]