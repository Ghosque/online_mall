import re

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
EXPIRE_SECONDS = 30  # 2 * 60 * 60
# Token刷新有效期：七天（当Token已过期但不超过七天则刷新新Token）
REFRESH_SECONDS = 60  # 7 * 24 * 60 * 60

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
             "PASSWORD": "redisserver",
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
    '127.0.0.1:9000',
    'localhost:9000',
    '121.32.145.115:63343'
)
CORS_ALLOW_CREDENTIALS = True  # 指明在跨域访问中，后端是否支持对cookie的操作
