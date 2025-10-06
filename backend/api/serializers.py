from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import Photo

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

# 图片上传序列化器
class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    thumbnail = serializers.ImageField(read_only=True)
    exif = serializers.JSONField(read_only=True)
    tags = serializers.JSONField(read_only=True)
    taken_at = serializers.DateTimeField(read_only=True)
    location = serializers.CharField(read_only=True)
    resolution = serializers.CharField(read_only=True)

    class Meta:
        model = Photo
        fields = [
            'id', 'user', 'image', 'thumbnail', 'description', 'uploaded_at',
            'exif', 'tags', 'taken_at', 'location', 'resolution'
        ]
        read_only_fields = ['id', 'user', 'uploaded_at', 'thumbnail', 'exif', 'tags', 'taken_at', 'location', 'resolution']

    def create(self, validated_data):
        from .exif_utils import extract_exif, get_datetime_location, generate_thumbnail
        image_file = validated_data['image']
        # 读取EXIF
        exif_data = None
        taken_at = None
        location = None
        resolution = None
        tags = []
        try:
            from io import BytesIO
            from datetime import datetime
            image_file.seek(0)
            img_bytes = BytesIO(image_file.read())
            exif_data = extract_exif(img_bytes)
            # 拍摄时间、经纬度
            dt, lat, lon = get_datetime_location(exif_data)
            taken_at = None
            if dt:
                dt_str = str(dt)
                tags.append(dt_str)  # 标签显示原始EXIF时间
                for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y:%m:%d %H:%M:%S.%f"):
                    try:
                        taken_at = datetime.strptime(dt_str, fmt)
                        break
                    except Exception:
                        continue
            # 标签示例：相机品牌、型号
            if lat and lon:
                location = f"{lat},{lon}"
            # 分辨率
            from PIL import Image
            img_bytes.seek(0)
            img = Image.open(img_bytes)
            resolution = f"{img.width}x{img.height}"
            # 标签示例：相机品牌、型号
            if 'Image Model' in exif_data:
                tags.append(exif_data['Image Model'])
            if 'Image Make' in exif_data:
                tags.append(exif_data['Image Make'])
        except Exception as e:
            exif_data = {}
        # 生成缩略图
        thumb_file = None
        try:
            image_file.seek(0)
            thumb_io = generate_thumbnail(image_file)
            from django.core.files.base import ContentFile
            thumb_file = ContentFile(thumb_io.read(), name=f"thumb_{image_file.name}")
        except Exception as e:
            thumb_file = None
        photo = Photo.objects.create(
            user=validated_data['user'],
            image=validated_data['image'],
            description=validated_data.get('description', ''),
            exif=exif_data,
            tags=tags,
            taken_at=taken_at,
            location=location,
            resolution=resolution,
        )
        if thumb_file:
            photo.thumbnail.save(thumb_file.name, thumb_file, save=True)
        return photo
