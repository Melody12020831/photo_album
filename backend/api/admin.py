from django.contrib import admin

# 可选：注册User模型，便于后台管理
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib import admin

admin.site.register(Token)
