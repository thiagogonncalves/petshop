"""
Reports URLs — read-only report endpoints.
"""
from django.urls import path
from .views import (
    SellersReportView,
    DashboardReportView,
    SalesReportView,
    ProductsSoldReportView,
    SalesRankingReportView,
    LowStockReportView,
    ABCProductsReportView,
    ServicesSoldReportView,
    TopClientsReportView,
    SalesHeatmapReportView,
    ProfitByProductReportView,
    SalesExportCSVView,
    ProductsSoldExportCSVView,
)

urlpatterns = [
    path('sellers/', SellersReportView.as_view(), name='reports-sellers'),
    path('dashboard/', DashboardReportView.as_view(), name='reports-dashboard'),
    path('sales/export.csv', SalesExportCSVView.as_view(), name='reports-sales-export-csv'),
    path('sales/', SalesReportView.as_view(), name='reports-sales'),
    path('products-sold/export.csv', ProductsSoldExportCSVView.as_view(), name='reports-products-sold-export-csv'),
    path('products-sold/', ProductsSoldReportView.as_view(), name='reports-products-sold'),
    path('sales-ranking/', SalesRankingReportView.as_view(), name='reports-sales-ranking'),
    path('low-stock/', LowStockReportView.as_view(), name='reports-low-stock'),
    path('abc-products/', ABCProductsReportView.as_view(), name='reports-abc-products'),
    path('services-sold/', ServicesSoldReportView.as_view(), name='reports-services-sold'),
    path('top-clients/', TopClientsReportView.as_view(), name='reports-top-clients'),
    path('sales-heatmap/', SalesHeatmapReportView.as_view(), name='reports-sales-heatmap'),
    path('profit-by-product/', ProfitByProductReportView.as_view(), name='reports-profit-by-product'),
]
