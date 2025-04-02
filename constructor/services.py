# constructor/services.py
import qrcode
import io
import os
from django.conf import settings
from django.core.files.base import ContentFile
from urllib.parse import urljoin


def generate_and_save_qr_code(custom_site):
    """
    Генерирует QR-код для сайта и сохраняет его в поле модели
    """
    # Формируем URL для публичного доступа к сайту
    site_url = urljoin(settings.FRONTEND_URL, f'/{custom_site.name}')

    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(site_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Сохраняем QR-код в байтовый поток
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Создаем имя файла для QR-кода
    filename = f"qr_code_{custom_site.id}_{custom_site.name}.png"

    # Сохраняем QR-код в поле модели
    custom_site.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)

    return site_url


def get_qr_code_url(custom_site):
    """
    Возвращает URL для QR-кода сайта или None если его нет
    """
    if custom_site.qr_code:
        return custom_site.qr_code.url
    return None