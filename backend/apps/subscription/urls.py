from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.subscription_status),
    path('pay/', views.subscription_pay),
    path('webhook/', views.mp_webhook),
]
