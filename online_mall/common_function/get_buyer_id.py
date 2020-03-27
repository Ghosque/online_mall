import re
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_jwt.utils import jwt_decode_handler


def get_buyer_id(token):
    token = re.search(settings.REGEX_TOKEN, token).group(1)
    token_info = jwt_decode_handler(token)
    user_id = token_info['user_id']
    buyer_id = User.objects.get(pk=user_id).buyer.id

    return buyer_id
