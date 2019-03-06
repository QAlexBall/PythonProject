from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from jianshu.models import User

class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        user_name = request.COOKIES.get('user_name')
        if user_name:
            request.user_name = user_name
