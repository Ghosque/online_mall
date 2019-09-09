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
from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from django.conf.urls.static import serve
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from common import views as c_views
from merchant import views as m_views


router = routers.DefaultRouter()

router.register(r'token_verify', c_views.TokenVerifyViewset, base_name='token_verify')
router.register(r'code', c_views.PhoneCodeViewset, base_name='verify_code')

router.register(r'merchantReg', m_views.MerchantRegViewset, base_name='merchant_reg')
router.register(r'merchantLogin', m_views.MerchantLoginViewset, base_name='merchant_login')
router.register(r'merchant', m_views.MerchantInfoViewset, base_name='merchant_info')
router.register(r'shopReg', m_views.ShopRegViewset, base_name='shop_reg')
router.register(r'shop', m_views.ShopInfoViewset, base_name='shop_info')
router.register(r'navigation', m_views.NavigationViewset, base_name='navigation')
router.register(r'category', m_views.CategoryViewset, base_name='category')


urlpatterns = [
    path('admin/', xadmin.site.urls, name='xadmin'),
    path('api/', include(router.urls)),
    path(r'api-token-auth/', obtain_jwt_token),
    url(r'media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),
]
