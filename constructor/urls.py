from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlockTypeViewSet,
    CustomSiteViewSet,
    TemplateCustomSiteView,
    TextBlockViewSet,
    ImageBlockViewSet,
    VideoBlockViewSet,
    CustomSiteCopyView,
)

# Создаем маршрутизатор для ModelViewSet
router = DefaultRouter()
router.register(r'block-types', BlockTypeViewSet, basename='block-type')
router.register(r'custom-sites', CustomSiteViewSet, basename='custom-site')
router.register(r'text-blocks', TextBlockViewSet, basename='text-block')
router.register(r'image-blocks', ImageBlockViewSet, basename='image-block')
router.register(r'video-blocks', VideoBlockViewSet, basename='video-block')

urlpatterns = [
    path('custom-site-template/', TemplateCustomSiteView.as_view(), name='custom-site-template'),
    path('custom-site-copy/', CustomSiteCopyView.as_view(), name='custom-site-copy'),
    # Включаем маршруты, сгенерированные роутером
    path('api/', include(router.urls)),
]