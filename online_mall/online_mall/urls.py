"""online_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from common.views import PhoneCodeViewset
from merchant.views import MerchantRegViewset, MerchantLoginViewset, MerchantViewset


router = routers.DefaultRouter()
router.register(r'code', PhoneCodeViewset, base_name='verify_code')
router.register(r'merchantReg', MerchantRegViewset, base_name='merchant_reg')
router.register(r'merchantLogin', MerchantLoginViewset, base_name='merchant_login')
router.register(r'merchant', MerchantViewset, base_name='merchant_login')


urlpatterns = [
    path('admin/', xadmin.site.urls, name='xadmin'),
    path('api/', include(router.urls)),
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token),
]
