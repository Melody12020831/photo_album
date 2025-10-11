from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, PhotoSerializer
from django.contrib.auth.models import User
import re
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from .models import Photo

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'message': '注册成功',
                    'token': token.key
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                # 处理数据库唯一性约束错误
                return Response({'error': '用户名或邮箱已存在，请更换后重试。'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 找回账号API（演示：返回用户名，实际应发送邮件）
class RecoverAccountView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({'detail': '邮箱格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            # 实际生产应发送邮件，这里仅返回用户名演示
            return Response({'username': user.username, 'msg': '找回成功，用户名已发送到邮箱（演示）'})
        except User.DoesNotExist:
            return Response({'detail': '该邮箱未注册'}, status=status.HTTP_404_NOT_FOUND)

# 图片上传API（需登录）
from rest_framework.parsers import MultiPartParser, FormParser

class PhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print('FILES:', request.FILES)
        print('DATA:', request.data)
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = PhotoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'msg': '图片上传成功', 'photo': serializer.data}, status=status.HTTP_201_CREATED)
        print('图片上传 serializer.errors:', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.generics import ListAPIView
from django.db.models.functions import TruncDate
# 获取当前用户所有图片API（需登录）
class PhotoListView(ListAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Photo.objects.filter(user=self.request.user)
        
        tags = self.request.query_params.get('tags')
        upload_date_start = self.request.query_params.get('upload_date_start')
        upload_date_end = self.request.query_params.get('upload_date_end')
        taken_date = self.request.query_params.get('taken_date')
        location = self.request.query_params.get('location')
        resolution = self.request.query_params.get('resolution')
        ratio = self.request.query_params.get('ratio')
        megapixel_str = self.request.query_params.get('megapixel')

        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            queryset = queryset.filter(tags__contains=tag_list)
        if upload_date_start:
            queryset = queryset.filter(uploaded_at__date__gte=upload_date_start)
        if upload_date_end:
            queryset = queryset.filter(uploaded_at__date__lte=upload_date_end)
        if taken_date:
            queryset = queryset.filter(taken_at__date=taken_date)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if resolution:
            queryset = queryset.filter(resolution__iexact=resolution)

        queryset = queryset.order_by('-uploaded_at')

        final_results = list(queryset)

        if ratio:
            from math import gcd
            def match_ratio(res):
                try:
                    w, h = [int(x) for x in res.split('x')]
                    if h == 0: return False
                    common_divisor = gcd(w, h)
                    r = f"{w//common_divisor}:{h//common_divisor}"
                    return r == ratio
                except (ValueError, IndexError, TypeError):
                    return False
            final_results = [p for p in final_results if p.resolution and match_ratio(p.resolution)]

        if megapixel_str:
            try:
                megapixel_gt = float(''.join(filter(str.isdigit, megapixel_str)))
            except ValueError:
                megapixel_gt = 0
                
            if megapixel_gt > 0:
                def match_mp(res):
                    try:
                        w, h = [int(x) for x in res.split('x')]
                        mp = (w * h) / 1_000_000
                        return mp > megapixel_gt
                    except (ValueError, IndexError, TypeError):
                        return False
                final_results = [p for p in final_results if p.resolution and match_mp(p.resolution)]
        
        return final_results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'photos': serializer.data})

    def get_serializer_context(self):
        return {'request': self.request}

# 删除图片API（需登录）
from rest_framework.generics import DestroyAPIView

class PhotoDeleteView(DestroyAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)