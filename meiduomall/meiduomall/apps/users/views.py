from django.shortcuts import render
from .models import User
from django.views import View
from django import http
import json
import re
from django_redis import get_redis_connection


# Create your views here.


class UserNameCountView(View):
    def get(self, request, username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class MobileCountView(View):
    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': '访问数据库失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'count': count})


class RegisterPage(View):
    def post(self, request):
        temp_dict = json.loads(request.body.decode())
        username = temp_dict['username']
        password = temp_dict['password']
        password2 = temp_dict['password2']
        mobile = temp_dict['mobile']
        allow = temp_dict['allow']
        sms_code_client = temp_dict['sms_code']

        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'}, json_dumps_params={'ensure_ascii': False})
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '密码格式有误'}, json_dumps_params={'ensure_ascii': False})
        if password != password2:
            return http.JsonResponse({'code': 400, 'errmsg': '密码两次输入不一致'}, json_dumps_params={'ensure_ascii': False})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '手机号格式有误'}, json_dumps_params={'ensure_ascii': False})
        if not allow:
            return http.JsonResponse({'code': 400, 'errmsg': 'allow格式有误'}, json_dumps_params={'ensure_ascii': False})
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if not sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码过期'}, json_dumps_params={'ensure_ascii': False})
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码不正确'}, json_dumps_params={'ensure_ascii': False})
        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': '保存到数据库出错'}, json_dumps_params={'ensure_ascii': False})
        return http.JsonResponse({'code': 0, 'errmsg': '用户注册成功'}, json_dumps_params={'ensure_ascii': False})