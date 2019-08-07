import json
import random
import string
from django.views.generic.base import View
from django.http import HttpResponse

from .models import Merchant


class MerchantView(View):

    def post(self, request):
        """
        商家注册、手机号验证、登录功能实现
        :param request: request请求
        :return: 返回JSON数据，包括一个状态码，0：表示失败，1：表示成功，2：表示传入请求的type参数不在范围内
        """
        type = request.POST.get('type')

        if type == 'login':
            content = self.do_login(request)

        elif type == 'register':
            content = self.do_register(request)

        elif type == 'get_verify':
            content = self.get_verify_code(request)

        else:
            content = {'code': 2}

        return HttpResponse(json.dumps(content, ensure_ascii=False), content_type="application/json,charset=utf-8")

    def do_login(self, request):
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        check_result = Merchant.check_password(phone, password)
        if check_result:
            merchant_id = check_result.merchant_id
            request.session['merchant'] = merchant_id
            content = {'code': 1}
        else:
            content = {'code': 0}

        return content

    def do_register(self, request):
        password = request.POST.get('password')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        phone = request.POST.get('phone')
        id_card = request.POST.get('id_card')

        data_dict = {
            'password': password,
            'name': name,
            'gender': gender,
            'age': age,
            'phone': phone,
            'id_card': id_card,
        }
        content = Merchant.insert_data(data_dict)

        return content

    def get_verify_code(self, request):
        verify_code = ''.join(random.sample(string.ascii_letters + string.digits, 6))

        request.session['verify_code'] = verify_code
        request.session.set_expiry(60 * 5)

        content = {'verify_code': verify_code}

        return content
