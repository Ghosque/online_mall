import json
import random
import string
from django.views.generic.base import View
from django.http import HttpResponse

from .models import Merchant, BackStageSecond


class CommonView(View):

    @classmethod
    def get_navigation_data(cls):
        context = {'navigator': {}}
        navigation_data = BackStageSecond.get_back_stage_data()
        for item in navigation_data:
            nav_first = item.first
            if nav_first.id not in context['navigator'].keys():
                context['navigator'][nav_first.id] = {
                    'nav_first_id': nav_first.id,
                    'nav_first_name': nav_first.name,
                    'nav_second': [{
                        'nav_second_id': item.id,
                        'nav_second_name': item.name,
                        'nav_second_status': item.status,
                    }]
                }

            else:
                context['navigator'][nav_first.id]['nav_second'].append({
                    'nav_second_id': item.id,
                    'nav_second_name': item.name,
                    'nav_second_status': item.status,
                })

        return context


class MerchantView(View):

    def post(self, request):
        """
        商家注册、手机号验证、登录功能实现
        :param request: request请求
        :return: 返回JSON数据，包括一个状态码，0：表示失败，1：表示成功，2：表示传入请求的type参数不在范围内
        """
        type = request.POST.get('type')

        if type == 'login':
            context = self.do_login(request)

        elif type == 'register':
            context = self.do_register(request)

        elif type == 'get_verify':
            context = self.get_verify_code(request)

        else:
            context = {'code': 2}

        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json,charset=utf-8")

    @staticmethod
    def do_login(request):
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        check_result = Merchant.check_password(phone, password)
        if check_result:
            merchant_id = check_result.merchant_id
            request.session['merchant'] = merchant_id
            context = {'code': 1}
        else:
            context = {'code': 0}

        return context

    @staticmethod
    def do_register(request):
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

    @staticmethod
    def get_verify_code(request):
        verify_code = ''.join(random.sample(string.ascii_letters + string.digits, 6))

        request.session['verify_code'] = verify_code
        request.session.set_expiry(60 * 5)

        content = {'verify_code': verify_code}

        return content


class BackStageView(CommonView):

    def get(self, request):
        context = self.get_navigation_data()

        return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json,charset=utf-8")


