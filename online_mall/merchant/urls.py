from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.MerchantView.as_view(), name='lregister'),
    path('getVerify/', views.MerchantView.as_view(), name='get_verify'),
    path('login/', views.MerchantView.as_view(), name='login'),

    path('common/', views.CommonView.as_view(), name='common'),
]
