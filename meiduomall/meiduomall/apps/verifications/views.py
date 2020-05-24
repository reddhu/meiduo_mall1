from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from meiduo_mall1.meiduomall.meiduomall.libs.captcha.captcha import captcha
from meiduo_mall1.meiduomall.meiduomall.libs.yuntongxun.ccp_sms import CCP
import logging
import random

logger = logging.getLogger('django')


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex(f'img_{uuid}', 300, text)
        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    def get(self, request, mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        if not all([image_code_client, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'}, json_dumps_params={'ensure_ascii':False})
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get(f'img_{uuid}')
        if image_code_server is None:
            return JsonResponse({'code': 400, 'errmsg': '图形验证码失效'}, json_dumps_params={'ensure_ascii':False})
        try:
            redis_conn.delete(f'img_{uuid}')
        except Exception as e:
            logger.error(e)
        image_code_server = image_code_server.decode()
        if image_code_server.lower() != image_code_client.lower():
            return JsonResponse({'code': 400, 'errmsg': '图形验证码输入错误'}, json_dumps_params={'ensure_ascii':False})
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        redis_conn.setex(f'sms_{mobile}', 300, sms_code)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        return JsonResponse({'code': 200, 'errmsg': '发送短信成功'}, json_dumps_params={'ensure_ascii': False})

# Create your views here.
