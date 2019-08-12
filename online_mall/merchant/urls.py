from django.urls import path, include

from . import views


urlpatterns = [
    path('merchants/', views.MerchantsList.as_view()),
    path('merchantDetail/', views.MerchantDetail.as_view()),
]
