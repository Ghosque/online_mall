from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.MerchantView.as_view(), name='lregister'),
    path('getVerify/', views.MerchantView.as_view(), name='get_verify'),
    path('login/', views.MerchantView.as_view(), name='login'),

    path('backStage/', views.BackStageView.as_view(), name='back_stage'),
]
