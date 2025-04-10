from django.db import models
from server.settings import *
from django.contrib.auth.models import User

class Patient(models.Model):
    id = models.AutoField(primary_key=True)# 防覆盖
    account =  models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    avator = models.CharField(max_length=255)# 头像url
    name = models.CharField(max_length=32)
    gender = models.CharField(max_length=8)
    age = models.CharField(max_length=8)


# class User(models.Model):
#     # username=username, password=password, email=email
#     phone = models.CharField(max_length=32)
#     email = models.EmailField(max_length=255)
#     username = models.CharField(max_length=32)
#     password = models.CharField(max_length=64)

class FaceDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detections')
    image = models.ImageField(upload_to='detections/')
    face_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection by {self.user.username} on {self.created_at}"

class DetectedFace(models.Model):
    detection = models.ForeignKey(FaceDetection, on_delete=models.CASCADE, related_name='faces')
    bbox = models.JSONField()  # 存储边界框坐标 [x1, y1, x2, y2]
    confidence = models.FloatField()

    def __str__(self):
        return f"Face in {self.detection}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user.username}"

class FaceLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_faces')
    name = models.CharField(max_length=100)  # 人脸对应的人名
    image = models.ImageField(upload_to='face_library/')  # 参考图像
    face_encoding = models.BinaryField()  # 存储人脸特征向量（二进制格式）
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Face of {self.name} (added by {self.user.username})"

class RecognizedFace(models.Model):
    detection = models.ForeignKey(DetectedFace, on_delete=models.CASCADE, related_name='recognitions')
    face_library = models.ForeignKey(FaceLibrary, on_delete=models.SET_NULL, null=True, related_name='recognitions')
    similarity = models.FloatField()  # 存储相似度分数

    def __str__(self):
        return f"Recognition in {self.detection.detection} - {self.similarity:.2f} similarity"
