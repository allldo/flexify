# Generated by Django 4.2.16 on 2025-06-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('constructor', '0004_customsite_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsite',
            name='theme',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
