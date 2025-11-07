from django.utils import timezone
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import requests

# MCP智能搜索API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mcp_search(request):
    """
    POST /api/search/mcp
    {"query": "去年夏天在海边拍的照片"}
    """
    user = request.user
    query = request.data.get('query', '').strip()
    if not query:
        return Response({'error': '请输入搜索内容'}, status=400)

    # 获取用户相册中所有已有的标签和描述信息，供大模型参考
    from .models import UserTag
    user_photos = Photo.objects.filter(user=user)
    
    # 收集所有不重复的标签
    all_tags = set()
    for photo in user_photos:
        if photo.tags:
            all_tags.update(photo.tags)
    
    # 收集所有不为空的描述（去重，最多取50条避免prompt过长）
    all_descriptions = []
    for photo in user_photos:
        if photo.description and photo.description.strip():
            desc = photo.description.strip()
            if desc not in all_descriptions:
                all_descriptions.append(desc)
                if len(all_descriptions) >= 50:
                    break
    
    # 构造System Prompt，包含用户相册的标签和描述信息
    today = timezone.now().date().isoformat()
    
    tags_info = f"用户相册中已有的标签：{', '.join(sorted(all_tags))}" if all_tags else "用户相册中暂无标签。"
    descriptions_info = f"用户相册中部分图片描述示例：\n" + "\n".join([f"- {desc}" for desc in all_descriptions[:10]]) if all_descriptions else "用户相册中暂无图片描述。"
    
    system_prompt = f"""
    你是一个智能相册助手。你的任务是将用户的自然语言查询转换为一个严格的 JSON 对象，用于数据库检索。
    今天是{today}。

    为了更好地理解用户的查询意图，以下是用户相册的现有信息：
    {tags_info}
    {descriptions_info}

    你必须返回以下格式的 JSON，字段不存在时返回 null：{{"tags": ["string"], "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD", "keywords": ["string"]}}
    字段映射规则：
    - tags: 从查询中提取的物体、场景、人物等名词标签。请优先使用用户相册中已有的标签，如果查询中的概念在已有标签中存在，请使用已有标签的准确名称。
    - date_from / date_to: 从查询中提取的时间范围 (如 "去年夏天" -> {{"date_from": "2024-06-01", "date_to": "2024-08-31"}}；"上周" -> ...)。
    - keywords: 描述性的词语，用于模糊搜索图片描述字段。请参考用户相册中已有的描述风格和用词。
    只返回JSON，不要任何解释。
    """

    # 使用豆包模型（OpenAI客户端）进行自然语言解析
    from openai import OpenAI
    api_key = "85fa8223-1fb5-4f2e-bbe5-90f8d1898c0f"  # 可改为 os.environ.get("DOUBAO_API_KEY")
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    model = "doubao-1.5-vision-lite-250315"  # 文本推理也可用此模型
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": system_prompt + "\n" + query}
                ]}
            ],
            max_tokens=300,
            temperature=0.2,
        )
        if not response.choices:
            raise ValueError("AI model returned no response.")
        llm_text = response.choices[0].message.content.strip()
    except Exception as e:
        return Response({'error': '智能助手暂时不可用，请稍后再试'}, status=503)

    # 解析LLM返回的JSON
    try:
        result = json.loads(llm_text)
        tags = result.get('tags') or []
        date_from = result.get('date_from')
        date_to = result.get('date_to')
        keywords = result.get('keywords') or []
    except Exception:
        return Response({'error': '智能助手暂时无法理解，请换个说法'}, status=200)

    # 构建数据库查询
    photos = Photo.objects.filter(user=user)
    if tags:
        for tag in tags:
            photos = photos.filter(tags__contains=[tag])
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            photos = photos.filter(taken_at__gte=date_from_obj)
        except Exception:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            photos = photos.filter(taken_at__lte=date_to_obj)
        except Exception:
            pass
    if keywords:
        for kw in keywords:
            photos = photos.filter(description__icontains=kw)

    photos = photos.order_by('-uploaded_at')
    serializer = PhotoSerializer(photos, many=True, context={'request': request})
    return Response({'photos': serializer.data})

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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import os
import threading
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_photo_tags(request):
    """
    更新指定图片的标签
    """
    user = request.user
    photo_id = request.data.get('photo_id')
    tags_list = request.data.get('tags', [])
    if not photo_id or not isinstance(tags_list, list):
        return Response({'error': '参数错误'}, status=400)
    
    try:
        photo = Photo.objects.get(id=photo_id, user=user)
    except Photo.DoesNotExist:
        return Response({'error': '图片不存在或无权限'}, status=404)

    photo.tags = tags_list
    for tag_name in tags_list:
        UserTag.objects.get_or_create(user=user, tag=tag_name)

    photo.save()
    # 返回更新后的标签列表
    serializer = PhotoSerializer(photo, context={'request': request})
    return Response({'msg': '标签已更新', 'photo': serializer.data})

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

import threading
from openai import OpenAI

def analyze_image_tags(image_url, model="doubao-1.5-vision-lite-250315", api_key=None, base_url=None):
    """
    调用AI模型分析图片标签。
    返回一个标签列表 (list of strings)。
    如果失败，则抛出异常。
    """
    if not api_key:
        raise ValueError("API key is missing.")
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    prompt = "请仔细分析这张图片的内容，返回5到10个最相关的描述性中文标签（例如：风景, 人物, 建筑, 天空, 海滩）。请只返回用英文逗号(,)分隔的标签字符串，不要包含任何其他说明性文字。"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=100, # 限制返回长度
        temperature=0.3, # 降低随机性，使其返回更固定的标签
    )

    if not response.choices:
        raise ValueError("AI model returned no response.")

    content = response.choices[0].message.content
    
    if not content:
        return []

    # 简单的清洗和解析
    # 移除可能的 markdown 符号或引号
    content = content.strip().strip("`").strip("'").strip('"')
    
    # AI有时可能返回 "标签：风景,人物" 或 "风景, 人物"
    # 我们只取冒号（中文或英文）后面的部分
    if '：' in content:
        content = content.split('：', 1)[-1]
    if ':' in content:
        content = content.split(':', 1)[-1]

    # 按逗号（中文或英文）分割，并去除空白
    tags_list = []
    for t in re.split(r'[,\uff0c]', content): # 同时按英文和中文逗号分割
        cleaned_tag = t.strip()
        if cleaned_tag:
            tags_list.append(cleaned_tag)
            
    return tags_list

class PhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print('FILES:', request.FILES)
        print('DATA:', request.data)
        
        try:
            # 不使用 .copy()，直接构造新字典，避免深拷贝文件对象
            data = {
                'user': request.user.id,
                'image': request.FILES.get('image'),
                'description': request.data.get('description', ''),
                'tags': request.data.get('tags', [])
            }
            
            serializer = PhotoSerializer(data=data, context={'request': request})
            
            if serializer.is_valid():
                photo = serializer.save(user=request.user)

                # 上传成功后，直接返回图片信息。
                # 前端接收到这个响应后，应弹窗询问用户是否进行AI分析。
                return Response({
                    'msg': '图片上传成功',
                    'photo': serializer.data,
                }, status=status.HTTP_201_CREATED)
            
            print('Serializer errors:', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f'Upload error: {type(e).__name__}: {str(e)}')
            import traceback
            traceback.print_exc()
            return Response({'error': f'上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# (新增) AI分析触发API
class AnalyzeTagsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        """
        触发对指定照片的AI标签分析。
        前端在用户同意分析后调用此接口。
        """
        try:
            photo = Photo.objects.get(pk=pk, user=request.user)
        except Photo.DoesNotExist:
            return Response({'error': '照片不存在或无权访问'}, status=status.HTTP_404_NOT_FOUND)

        if not photo.image or not hasattr(photo.image, 'url'):
            return Response({'error': '照片文件不存在URL'}, status=status.HTTP_400_BAD_REQUEST)

        # 从环境变量获取正确的 Key
        api_key = "85fa8223-1fb5-4f2e-bbe5-90f8d1898c0f" 
        # api_key = os.environ.get("DOUBAO_API_KEY") 
        if not api_key:
            print("错误：DOUBAO_API_KEY 环境变量未设置。")
            return Response({'error': 'AI服务配置错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        image_url = request.build_absolute_uri(photo.image.url) # 确保是绝对路径

        try:
            # 调试日志：打印 Django 认为的路径
            print(f"[DEBUG] 尝试读取文件。MEDIA_ROOT: {settings.MEDIA_ROOT}")
            print(f"[DEBUG] 数据库中的文件名 (photo.image.name): {photo.image.name}")
            print(f"[DEBUG] 尝试打开的绝对路径 (photo.image.path): {photo.image.path}")
            
            # 1. 检查文件是否存在
            if not photo.image.storage.exists(photo.image.name):
                print(f"[DEBUG] 错误：photo.image.storage.exists() 返回 False")
                return Response({'error': '图片文件在存储中不存在'}, status=status.HTTP_404_NOT_FOUND)

            # 2. 读取图片文件的原始字节
            print("[DEBUG] 文件存在，尝试打开...")
            with photo.image.open('rb') as f:
                image_bytes = f.read()
            print("[DEBUG] 文件读取成功。")
            
            # 3. 将字节编码为 Base64 字符串
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # 4. 猜测文件的 MIME 类型 (例如 'image/png' 或 'image/jpeg')
            mime_type, _ = mimetypes.guess_type(photo.image.name)
            if not mime_type:
                mime_type = 'image/png' # 如果猜不到，给一个默认值
            
            # 5. 创建 Base64 Data URL
            image_data_url = f"data:{mime_type};base64,{base64_data}"
            print("[DEBUG] Base64 编码成功。")

        except Exception as e:
            print("="*50)
            print(f"[!!! 严重错误 !!!] 读取或编码图片文件失败:")
            print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
            print(f"尝试读取的 photo.image.name: {photo.image.name}")
            try:
                print(f"尝试读取的 photo.image.path: {photo.image.path}")
            except Exception as pe:
                print(f"获取 photo.image.path 时也出错: {pe}")
            print(f"Python 异常类型: {type(e).__name__}")
            print(f"Python 异常信息: {e}")
            print("="*50)
            
            return Response({'error': '服务器读取图片文件失败，请检查后端日志'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # 同步调用AI分析，因为前端正在等待这个结果
            suggested_tags = analyze_image_tags(
                image_url=image_data_url, # <--- 传递 Base64 data URL
                api_key=api_key, 
                base_url=base_url
            )
            
            if not suggested_tags:
                return Response({
                    'msg': 'AI未分析出任何标签',
                    'suggested_tags': []
                }, status=status.HTTP_200_OK)

            # 成功返回建议的标签列表
            return Response({
                'msg': 'AI分析完成',
                'suggested_tags': suggested_tags
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"AI分析失败: {e}")
            # 向前端返回一个通用错误
            return Response({'error': f'AI分析失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"AI分析失败: {e}")
            # 向前端返回一个通用错误
            return Response({'error': f'AI分析失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                q_obj |= Q(tags__contains=tag)
            queryset = queryset.filter(q_obj).distinct()
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
    
from django.core.files.base import ContentFile
import os
from django.conf import settings
import base64
import mimetypes

class PhotoEditView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk=None):
        try:
            # 确保用户只能修改自己的照片
            photo = Photo.objects.get(pk=pk, user=request.user)
        except Photo.DoesNotExist:
            return Response({'error': '照片不存在或无权修改'}, status=status.HTTP_404_NOT_FOUND)

        new_image = request.FILES.get('image')
        if not new_image:
            return Response({'error': '未提供新的图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 删除旧的物理文件
        if photo.image and hasattr(photo.image, 'path'):
            old_path = photo.image.path
            if os.path.isfile(old_path):
                os.remove(old_path)
        
        # 2. 保存新文件
        # Django 会自动处理文件名冲突并保存到 MEDIA_ROOT 下的 upload_to 目录
        photo.image.save(new_image.name, new_image, save=True)

        # 3. （可选）更新其他元数据，比如分辨率
        #    如果需要，可以在这里重新用 Pillow 读取新图片并更新 photo.resolution 字段
        
        # 4. 返回包含新图片 URL 的响应
        serializer = PhotoSerializer(photo, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)