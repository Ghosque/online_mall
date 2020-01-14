from rest_framework.response import Response
from rest_framework import viewsets

from .models import Buyer


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'auth':
            self.handle_auth(request)

        elif type == 'login':
            self.handle_login(request)

        else:
            pass

    @classmethod
    def handle_auth(cls, request):
        pass

    @classmethod
    def handle_login(cls, request):
        pass
