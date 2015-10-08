# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url, include

from rest_framework import routers

from sanza.Store.api import (
    SaleItemViewSet, StoreItemViewSet, StoreItemCategoryViewSet, StoreItemTagViewSet, CartView, FavoriteView
)
from sanza.Store.admin import export_stock, export_stock_alert
from sanza.Store.views.sales_documents import (
    SalesDocumentView, SalesDocumentPdfView, SalesDocumentPublicView
)


store_items_router = routers.DefaultRouter()
store_items_router.register(r'store-items', StoreItemViewSet, base_name='store_store-items')
store_items_router.register(r'categories', StoreItemCategoryViewSet)
store_items_router.register(r'tags', StoreItemTagViewSet)


sales_items_router = routers.DefaultRouter()
sales_items_router.register(r'sales-items', SaleItemViewSet)


urlpatterns = patterns('sanza.Store.views',
    url(
        r'^view-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(),
        name='store_view_sales_document'
    ),

    url(
        r'^document/(?P<action_uuid>[\w\d-]+)/$',
        SalesDocumentPublicView.as_view(),
        name='store_view_sales_document_public'
    ),

    url(
        r'^view-sales-document/(?P<action_id>\d+)/pdf/$',
        SalesDocumentPdfView.as_view(),
        name='store_view_sales_document_pdf'
    ),

    url(
        r'^api/cart/$',
        CartView.as_view(),
        name='store_post_cart'
    ),

    url(
        r'^api/favorites/$',
        FavoriteView.as_view(),
        name='store_favorites_api'
    ),

    url(r'^api/', include(store_items_router.urls)),

    url(r'^api/(?P<action_id>\d+)/', include(sales_items_router.urls)),

    url(r"^admin/export-stock/$", export_stock, name='store_store_item_admin_export'),
    url(
        r"^admin/export-stock-alert/$",
        export_stock_alert,
        name='store_store_item_admin_export_alert'
    )
)