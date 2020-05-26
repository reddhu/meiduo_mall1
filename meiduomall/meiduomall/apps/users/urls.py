from django.urls import re_path, path
from .views import UserNameCountView, RegisterPage, MobileCountView, LoginView

urlpatterns = [
    re_path(r'^usernames/(?P<username>\w{5,20}/count/$)', UserNameCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterPage.as_view())
]