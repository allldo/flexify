import json
from urllib.parse import urljoin

from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from constructor.models import  CustomSite, Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'block_type', 'order', 'created_at', 'custom_sites_link', 'owner')
    list_filter = ('type', 'created_at')
    search_fields = ('id', 'type', 'data', 'custom_sites__user__phone_number')
    readonly_fields = ('created_at', 'owner', 'custom_sites_display')
    fieldsets = (
        ('Basic Information', {
            'fields': ('type', 'order', 'data', 'created_at')
        }),
        ('Associated Sites', {
            'fields': ('custom_sites_display',),
        }),
    )

    def block_type(self, obj):
        block_types_icons = {
            'text': '📝',
            'image': '🖼️',
            'gif': '🎞️',
            'qanda': '❓',
            'social': '👥',
            'video': '🎬',
            'profile': '👤',
            'product': '🛍️',
            'link': '🔗',
            'quote': '💬',
            'contacts': '📞',
            'delimiter': '➖',
            'gallery': '🖼️',
            'mix': '🔄'
        }
        icon = block_types_icons.get(obj.type, '📄')
        return format_html('{} {}', icon, obj.type)

    block_type.short_description = 'Type'

    def custom_sites_link(self, obj):
        sites = obj.custom_sites.all()
        if not sites:
            return '-'
        links = []
        for site in sites[:3]:  # Limit to 3 sites to avoid cluttering
            url = reverse('admin:constructor_customsite_change', args=[site.id])
            links.append(f'<a href="{url}">{site.name}</a>')

        more_count = sites.count() - 3
        if more_count > 0:
            links.append(f'and {more_count} more')

        return mark_safe(', '.join(links))

    custom_sites_link.short_description = 'Sites'

    def custom_sites_display(self, obj):
        sites = obj.custom_sites.all()
        if not sites:
            return '-'

        html = '<ul>'
        for site in sites:
            url = reverse('admin:constructor_customsite_change', args=[site.id])
            html += f'<li><a href="{url}">{site.name}</a></li>'
        html += '</ul>'

        return mark_safe(html)

    custom_sites_display.short_description = 'Associated Sites'

    def owner(self, obj):
        owner = obj.get_owner()
        if not owner:
            return '-'
        url = reverse('admin:cabinet_customuser_change', args=[owner.id])
        return format_html('<a href="{}">{}</a>', url, owner)

    owner.short_description = 'Owner'


@admin.register(CustomSite)
class CustomSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_template', 'block_count', 'created_at', 'qr_code_preview')
    list_filter = ('is_template', 'created_at')
    search_fields = ('name', 'user__email', 'user__phone_number')
    readonly_fields = ('created_at', 'blocks_list', 'qr_code_display', 'site_url')
    filter_horizontal = ('blocks',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'is_template', 'created_at')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_display', 'site_url'),
        }),
        ('Blocks', {
            'fields': ('blocks', 'blocks_list'),
        }),
    )

    def block_count(self, obj):
        count = obj.blocks.count()
        return count

    block_count.short_description = 'Blocks'

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" height="30" />')
        return '-'

    qr_code_preview.short_description = 'QR'

    def qr_code_display(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" height="200" /><br/>'
                             f'<a href="{obj.qr_code.url}" target="_blank">Открыть QR-код</a>')
        return 'QR-код еще не сгенерирован'

    qr_code_display.short_description = 'QR-код предпросмотр'

    def site_url(self, obj):
        url = urljoin(settings.FRONTEND_URL, f'/{obj.name}')
        return mark_safe(f'<a href="{url}" target="_blank">{url}</a>')

    site_url.short_description = 'URL сайта'

    def blocks_list(self, obj):
        blocks = obj.blocks.all().order_by('order')
        if not blocks:
            return 'No blocks'

        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr><th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Order</th>'
        html += '<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Type</th>'
        html += '<th style="text-align:left; padding:8px; border-bottom:1px solid #ddd;">Data</th></tr>'

        for block in blocks:
            url = reverse('admin:constructor_block_change', args=[block.id])
            html += f'<tr style="border-bottom:1px solid #eee;">'
            html += f'<td style="padding:8px;">{block.order}</td>'
            html += f'<td style="padding:8px;"><a href="{url}">{block.type}</a></td>'

            # Simplified data preview
            data_preview = str(block.data)
            if len(data_preview) > 100:
                data_preview = data_preview[:100] + '...'

            html += f'<td style="padding:8px;">{data_preview}</td>'
            html += '</tr>'

        html += '</table>'
        return mark_safe(html)

    blocks_list.short_description = 'Blocks List'

    def save_model(self, request, obj, form, change):
        """
        Переопределяем метод сохранения модели в админке,
        чтобы автоматически генерировать QR-код при необходимости
        """
        super().save_model(request, obj, form, change)

        # Если QR-код отсутствует или имя сайта изменилось, генерируем новый QR-код
        if not obj.qr_code or (change and 'name' in form.changed_data):
            from constructor.services import generate_and_save_qr_code
            generate_and_save_qr_code(obj)