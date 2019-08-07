from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.MerchantView.as_view(), name='login'),
]
