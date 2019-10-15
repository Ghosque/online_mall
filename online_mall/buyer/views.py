from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


class BuyerViewset(viewsets.ViewSet):

    def create(self, request):
        type = request.GET.get('type')

        if type == 'login':
            self.handle_login(request)

        elif type == 'register':
            self.handle_register(request)

        else:
            pass

    @classmethod
    def handle_login(cls, request):
        pass

    @classmethod
    def handle_register(cls, request):
        pass

    @permission_classes([IsAuthenticated])
    def retrieve(self, request, pk):
        pass
