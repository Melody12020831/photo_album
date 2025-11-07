from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json

from .models import Photo, UserTag # 导入 UserTag

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已存在')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        data['user'] = user
        return data
    
# 用于照片信息更新的序列化器
class PhotoUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.JSONField(required=False)
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)

    class Meta:
        model = Photo
        fields = ['description', 'tags']

    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("标签必须是列表格式。")
        # 确保标签库中有这些标签，并为用户创建新标签
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            for tag_name in value:
                UserTag.objects.get_or_create(user=request.user, tag=tag_name)
        return value

# 图片上传序列化器
class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    thumbnail = serializers.ImageField(read_only=True)
    exif = serializers.JSONField(read_only=True)
    tags = serializers.JSONField(required=False)

    def validate_tags(self, value):
        """
        一个更健壮的标签验证方法，可以处理多种输入格式。
        1. 如果已经是列表，直接返回。
        2. 如果是字符串，尝试按 JSON 解析。
        3. 如果 JSON 解析失败，则视为单个标签。
        始终返回一个字符串列表。
        """
        if not value:
            return []
        
        # 如果值已经是列表（例如，在其他API调用中），确保所有元素都是字符串
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]

        # 如果值是字符串，这是来自前端表单的常见情况
        if isinstance(value, str):
            try:
                # 尝试将其解析为JSON。这对应前端的 JSON.stringify(tags)
                tags_list = json.loads(value)
                if isinstance(tags_list, list):
                    return [str(v).strip() for v in tags_list if str(v).strip()]
                # 如果JSON解析结果不是列表，则将其视为单个标签
                return [str(tags_list).strip()] if str(tags_list).strip() else []
            except json.JSONDecodeError:
                # 如果它不是有效的JSON，就把它当作一个普通的字符串标签
                return [tag.strip() for tag in value.split(',') if tag.strip()]

        # 对于任何其他意外类型，返回一个空列表
        return []
    
    taken_at = serializers.DateTimeField(read_only=True)
    location = serializers.CharField(read_only=True)
    resolution = serializers.CharField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'user', 'image', 'thumbnail', 'description', 'uploaded_at',
            'exif', 'tags', 'taken_at', 'location', 'resolution'
        ]
        read_only_fields = ['id', 'user', 'uploaded_at', 'thumbnail', 'exif', 'taken_at', 'location', 'resolution']

    def create(self, validated_data):
        from .exif_utils import extract_exif, get_datetime_location, generate_thumbnail
        image_file = validated_data['image']
        exif_data = None
        taken_at = None
        location = None
        resolution = None
        
        # 首先获取用户提交的标签，确保是列表类型
        tags = validated_data.get('tags', [])
        if not isinstance(tags, list):
            tags = []
        
        try:
            from io import BytesIO
            from datetime import datetime
            image_file.seek(0)
            img_bytes = BytesIO(image_file.read())
            exif_data = extract_exif(img_bytes)
            dt, lat, lon = get_datetime_location(exif_data)
            
            # 如果存在拍摄日期，则追加到标签列表
            if dt:
                dt_str = str(dt)
                tags.append(dt_str) # <-- 修改点：直接 append
                # 只要 EXIF 有拍摄时间就写入 taken_at
                for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y:%m:%d %H:%M:%S.%f"):
                    try:
                        taken_at = datetime.strptime(dt_str, fmt)
                        break
                    except Exception:
                        continue
            
            if lat and lon:
                location = f"{lat},{lon}"
            
            from PIL import Image
            img_bytes.seek(0)
            img = Image.open(img_bytes)
            resolution = f"{img.width}x{img.height}"
            
            # 如果存在相机型号，则追加到标签列表
            if 'Image Model' in exif_data:
                tags.append(exif_data['Image Model']) # <-- 修改点：直接 append
            
            # 如果存在相机制造商，则追加到标签列表
            if 'Image Make' in exif_data:
                tags.append(exif_data['Image Make']) # <-- 修改点：直接 append
                
        except Exception:
            exif_data = {}
            
        thumb_file = None
        try:
            image_file.seek(0)
            thumb_io = generate_thumbnail(image_file)
            from django.core.files.base import ContentFile
            thumb_file = ContentFile(thumb_io.read(), name=f"thumb_{image_file.name}")
        except Exception:
            thumb_file = None
            
        unique_tags = list(dict.fromkeys(tags))
        
        # 保证 taken_at 字段有值（有 EXIF 就填，无则为 None）
        photo = Photo.objects.create(
            user=validated_data['user'],
            image=validated_data['image'],
            description=validated_data.get('description', ''),
            exif=exif_data,
            tags=unique_tags,
            taken_at=taken_at,
            location=location,
            resolution=resolution,
        )
        if thumb_file:
            photo.thumbnail.save(thumb_file.name, thumb_file, save=True)
        return photo
