from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, PhotoSerializer, PhotoUpdateSerializer
from django.contrib.auth.models import User
import re
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from .models import Photo
from .models import UserTag
from rest_framework.generics import UpdateAPIView

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
            photo = serializer.save(user=request.user)
            # 从验证后的数据中获取干净的标签列表
            validated_tags = serializer.validated_data.get('tags', [])
            if validated_tags:
                UserTag.objects.bulk_create([
                    UserTag(user=request.user, tag=tag)
                    for tag in validated_tags
                    if not UserTag.objects.filter(user=request.user, tag=tag).exists()
                ], ignore_conflicts=True)
            return Response({'msg': '图片上传成功', 'photo': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PhotoUpdateView(UpdateAPIView):
    serializer_class = PhotoUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 确保用户只能修改自己的照片
        return Photo.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}
    
class UserTagView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tags = UserTag.objects.filter(user=request.user).values_list('tag', flat=True).distinct()
        return Response({'tags': sorted(list(tags))})

    def post(self, request):
        tag_name = request.data.get('tag', '').strip()
        if not tag_name:
            return Response({'error': '标签名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用 get_or_create 避免重复，并返回创建状态
        tag, created = UserTag.objects.get_or_create(user=request.user, tag=tag_name)
        
        if created:
            return Response({'tag': tag.tag, 'msg': '标签创建成功'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'tag': tag.tag, 'msg': '标签已存在'}, status=status.HTTP_200_OK)

    def put(self, request):
        old_tag = request.data.get('old_tag', '').strip()
        new_tag = request.data.get('new_tag', '').strip()
        if not old_tag or not new_tag:
            return Response({'error': '标签名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            utag = UserTag.objects.get(user=request.user, tag=old_tag)
            utag.tag = new_tag
            utag.save()
            return Response({'msg': '标签修改成功'})
        except UserTag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        tag = request.data.get('tag', '').strip()
        if not tag:
            return Response({'error': '标签名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        UserTag.objects.filter(user=request.user, tag=tag).delete()
        return Response({'msg': '标签删除成功'})
    
    def post(self, request):
        tag_name = request.data.get('tag', '').strip()
        if not tag_name:
            return Response({'error': '标签名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用 get_or_create 避免重复，并返回创建状态
        tag, created = UserTag.objects.get_or_create(user=request.user, tag=tag_name)
        
        if created:
            return Response({'tag': tag.tag, 'msg': '标签创建成功'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'tag': tag.tag, 'msg': '标签已存在'}, status=status.HTTP_200_OK)
    
from rest_framework.generics import ListAPIView
from django.db.models.functions import TruncDate

# 获取当前用户所有图片API（需登录）
class PhotoListView(ListAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Photo.objects.filter(user=self.request.user)
        tags = self.request.query_params.get('tags')
        description = self.request.query_params.get('description')
        
        if tags:
            from django.db.models import Q
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            q_obj = Q()
            for tag in tag_list:
                q_obj |= Q(tags__contains=[tag])
            queryset = queryset.filter(q_obj)
        if description:
            queryset = queryset.filter(description__icontains=description)
            
        upload_date_start = self.request.query_params.get('upload_date_start')
        upload_date_end = self.request.query_params.get('upload_date_end')
        taken_date = self.request.query_params.get('taken_date')
        location = self.request.query_params.get('location')
        resolution = self.request.query_params.get('resolution')
        ratio = self.request.query_params.get('ratio')
        megapixel_str = self.request.query_params.get('megapixel')
        
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