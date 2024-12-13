from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomSiteViewSet,
    TemplateCustomSiteView,
    CustomSiteCopyView, BlockView, DeleteBlockView, ReArrangeBlocksView,
)

router = DefaultRouter()
router.register(r'custom-sites', CustomSiteViewSet, basename='custom-site')

urlpatterns = [
    path('custom-site-template/', TemplateCustomSiteView.as_view(), name='custom-site-template'),
    path('custom-site-copy/', CustomSiteCopyView.as_view(), name='custom-site-copy'),
    path('sites/<int:site_id>/block/', BlockView.as_view(), name='block'),
    path('sites/<int:site_id>/block/<int:block_id>/', DeleteBlockView.as_view(), name='delete_block'),
    path('sites/rearrange/', ReArrangeBlocksView.as_view(), name='rearrange'),

    path('api/', include(router.urls)),
]