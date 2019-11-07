import re
import oss2

from .base import *


ALLOWED_HOSTS = ['*']
# DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'online_mall',
        'USER': 'root',
        'PASSWORD': 'mysql',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ]
}

# Token过期时间：两小时
EXPIRE_SECONDS = 2 * 60 * 60
# Token刷新有效期：七天（当Token已过期但不超过七天则刷新新Token）
REFRESH_SECONDS = 7 * 24 * 60 * 60

# 自定义token过期时间
from _datetime import timedelta
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(seconds=EXPIRE_SECONDS),  # 过期时间：两小时
    'JWT_AUTH_HEADER_PREFIX': 'JWT',  # 设置请求头中的前缀
    'JWT_ALLOW_REFRESH': True,
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
             "PASSWORD": "Ghosque2580",
        },
    },
}

REDIS_TIMEOUT = 7 * 24 * 60 * 60
CUBES_REDIS_TIMEOUT = 60 * 60
NEVER_REDIS_TIMEOUT = 365 * 24 * 60 * 60

# 身份证最后一位校验数据
COEFFICIENT_LIST = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
REMAINDER_DICT = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7

IMPORT_EXPORT_USE_TRANSACTIONS = True

# 手机号码的验证正则表达式
REGEX_PHONE = re.compile("^1[358]\d{9}$|^147\d{8}$|^176\d{8}$")
# Token提取正则表达式
REGEX_TOKEN = re.compile("JWT (.*)")

APPEND_SLASH = False

CODE_VALIDATION = 5 * 60

# CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:9000',
    'http://localhost:9000',
    'http://localhost:63343',
)
CORS_ALLOW_CREDENTIALS = True  # 指明在跨域访问中，后端是否支持对cookie的操作
CORS_ORIGIN_ALLOW_ALL = True

# 图片库缓存时间
IMAGES_REFRESH_SECONDS = 4 * 60 * 60

# 分类状态码
CATEGORY_DELETE_STATUS = 0
CATEGORY_NORMAL_STATUS = 1
# 商店状态码
SHOP_DELETE_STATUS = 0
SHOP_NORMAL_STATUS = 1
SHOP_IN_REVIEW_STATUS = 2
# 商品状态码
COMMODITY_DELETE_STATUS = 0
COMMODITY_NORMAL_STATUS = 1
COMMODITY_IN_REVIEW_STATUS = 2
COMMODITY_OFF_SHELF_STATUS = 3
# 图片类型
COVER_IMAGE = 0
DISPLAY_IMAGE = 1
COLOR_IMAGE = 2

# Ali OSS
ACCESS_KEY_ID = "LTAI4FwfrskcFinuqtNADg8Y"
ACCESS_KEY_SECRET = "LrI2TbPEl467zC8qSgDpA87qIpDzsA"
END_POINT = "oss-cn-shenzhen.aliyuncs.com"
PREFIX_URL = 'http://'
BUCKET_NAME = "ghosque-online-mall"
BUCKET_ACL_TYPE = "private"
DEFAULT_FILE_STORAGE = 'aliyun_oss2_storage.backends.AliyunMediaStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = "media"

OSS_AUTH = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
OSS_ENDPOINT = PREFIX_URL + END_POINT
OSS_BUCKET = oss2.Bucket(OSS_AUTH, OSS_ENDPOINT, BUCKET_NAME)
