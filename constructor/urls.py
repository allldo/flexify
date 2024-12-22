from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomSiteViewSet,
    TemplateCustomSiteView,
    CustomSiteCopyView, BlockView, ReArrangeBlocksView, BlockViewSet, PublicSiteView
)

router = DefaultRouter()
router.register(r'custom-sites', CustomSiteViewSet, basename='custom-site')
router.register(r'blocks', BlockViewSet, basename='block')

urlpatterns = [
    path('custom-site-template/', TemplateCustomSiteView.as_view(), name='custom-site-template'),
    path('custom-site-copy/', CustomSiteCopyView.as_view(), name='custom-site-copy'),
    path('sites/<int:site_id>/block/', BlockView.as_view(), name='block'),
    path('sites/rearrange/', ReArrangeBlocksView.as_view(), name='rearrange'),
    path('site/view/<str:site_name>', PublicSiteView.as_view(), name='public_view'),
    path('api/', include(router.urls)),
]