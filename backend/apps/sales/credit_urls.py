"""
Crediário URLs - /api/credits/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditAccountViewSet, CreditInstallmentViewSet

router = DefaultRouter()
router.register(r'', CreditAccountViewSet, basename='credit')

# Pay installment must be before router to avoid matching <pk> as "installments"
urlpatterns = [
    path(
        'installments/<int:pk>/pay/',
        CreditInstallmentViewSet.as_view({'post': 'pay'}),
        name='credit-installment-pay'
    ),
    path('', include(router.urls)),
]
