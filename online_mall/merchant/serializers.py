from rest_framework import serializers
from .models import Merchant, Shop


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = "__all__"


class MerchantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ("phone", "password")


class ShopSerializer(serializers.ModelSerializer):
    merchant_id = serializers.IntegerField()

    class Meta:
        model = Shop
        fields = ("id", "shop_id", "name", "merchant_id")
