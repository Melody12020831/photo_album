from django.db import models

from django.contrib.auth.models import User

# 用户上传图片模型
class Photo(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
	image = models.ImageField(upload_to='photos/')
	thumbnail = models.ImageField(upload_to='photos/thumbnails/', blank=True, null=True)
	exif = models.JSONField(blank=True, null=True)
	tags = models.JSONField(blank=True, null=True, help_text='自动标签')
	taken_at = models.DateTimeField(blank=True, null=True, help_text='拍摄时间')
	location = models.CharField(max_length=255, blank=True, null=True, help_text='拍摄地点')
	resolution = models.CharField(max_length=32, blank=True, null=True, help_text='分辨率')
	description = models.CharField(max_length=255, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user.username} - {self.image.name}"

	def delete(self, *args, **kwargs):
		# 删除图片文件
		storage = self.image.storage
		image_path = self.image.path
		super().delete(*args, **kwargs)
		if storage.exists(image_path):
			storage.delete(image_path)

# Create your models here.
