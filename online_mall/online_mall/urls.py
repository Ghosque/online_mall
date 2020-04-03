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
from buyer import views as b_views
from payment import views as p_views


router = routers.DefaultRouter()

router.register(r'token_verify', c_views.TokenVerifyViewset, base_name='token_verify')
router.register(r'code', c_views.PhoneCodeViewset, base_name='verify_code')
router.register(r'color', c_views.ColorViewset, base_name='color')
router.register(r'merchantCommodity', c_views.CommodityViewset, base_name='commodity')
router.register(r'buyerNote', c_views.NoteViewset, base_name='note')
router.register(r'buyerCommodity', c_views.BuyerCommodityViewset, base_name='buyer_commodity')
router.register(r'followCommodity', c_views.CommodityFollowViewset, base_name='follow_commodity')
router.register(r'buyerTrace', c_views.BuyerTraceViewset, base_name='buyer_trace')

router.register(r'merchant', m_views.MerchantViewset, base_name='merchant')
router.register(r'merchantShop', m_views.ShopViewset, base_name='shop_info')
router.register(r'merchantNavigation', m_views.NavigationViewset, base_name='navigation')
router.register(r'merchantCategory', m_views.CategoryViewset, base_name='category')
router.register(r'merchantImage', m_views.ImageViewset, base_name='image_upload')

router.register(r'buyer', b_views.BuyerViewset, base_name='buyer')
router.register(r'address', b_views.AddressViewset, base_name='address')

router.register(r'cart', p_views.ShoppingCartViewset, base_name='shopping_cart')
router.register(r'order', p_views.OrderViewset, base_name='order')


urlpatterns = [
    path('admin/', xadmin.site.urls, name='xadmin'),
    path('api/', include(router.urls)),
    path(r'api-token-auth/', obtain_jwt_token),
    url(r'media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),
]
