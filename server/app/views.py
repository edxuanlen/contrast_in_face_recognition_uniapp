from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from server.settings import STATICFILES_DIRS
from app import pred
from django.conf import settings
import os
from app.models import *
from datetime import datetime, timedelta
import json
import os
import time
import random
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
import cv2
import numpy as np
import torch
from PIL import Image
import platform
from pathlib import Path

# 在加载模型之前添加这段代码
if platform.system() == 'Windows':
    # 在Windows上修复PosixPath问题
    import pathlib
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

# 然后再加载模型
model = torch.hub.load('ultralytics/yolov5', 'custom', path='app/yolov5/weights/face_detection.pt', force_reload=False)
model.conf = 0.5  # 设置置信度阈值

def class_tumor_list(request):
    class_tumor_data = {
                        0: '未检测到异常',
                        1: 'Ⅰ型肿瘤',
                        2: 'Ⅱ型肿瘤'
                    }
    for k, v in class_tumor_data.items():
        class_tumor.objects.create(class_id=k, class_name=v)

    return JsonResponse({'name':200})

def tmour_pred(request):
    img = request.FILES.get('file')
    fs = FileSystemStorage(location='static/tmour')
    fname = fs.save(img.name, img)
    image_url,cls,boxs=pred.tmourdetect(os.path.join(STATICFILES_DIRS[2], fname))
    # image_url,cls,boxs=pred.tmourdetect(os.path.join(STATICFILES_DIRS[0], 'result.jpg'))
    absolute_image_url = request.build_absolute_uri(image_url)
    # absolute_image_url = os.path.join(STATICFILES_DIRS[0], 'result.jpg'),
    obj = class_tumor.objects.get(class_id=cls)
    name = obj.class_name
    print(absolute_image_url)
    current_time = datetime.now().strftime("%Y-%m-%d %H::%M:%S")
    ailog = data_tumor(
        user_id = 666,
        aitype = 2,
        cls_type = cls, # 检测结果 0 未检测
        cls_name = name,
        imgpath = absolute_image_url,
        img_bbox = boxs, # 检测框
        result_time = current_time,
    )
    ailog.save()
    return JsonResponse({'code':200,'path': absolute_image_url,'name': name})

def tmourdelete(request):
    ids = request.GET.get('id')
    obj = data_tumor.objects.get(id=ids,delete_mask=1)
    if obj is None: return JsonResponse({'data': '没有此数据'})
    obj.delete_mask = 0
    obj.save()
    obj = data_skin.objects.filter(id=ids,delete_mask=1).exists()
    if obj == 0 : return JsonResponse({'data': '删除成功'})
    return JsonResponse({'data': '删除失败'})

def tmour_preds(request):
    imgs = request.FILES.getlist('file')
    fs = FileSystemStorage(location='static/tmour')
    urls = []
    names = []
    for img in imgs:
        fname = fs.save(img.name, img)
        image_url,cls,boxs=pred.tmourdetect(os.path.join(STATICFILES_DIRS[2], fname))
        absolute_image_url = request.build_absolute_uri(image_url)
        current_time = datetime.now().strftime("%Y-%m-%d %H::%M:%S")
        obj = class_tumor.objects.get(class_id=cls)
        name = obj.class_name
        ailog = data_tumor(
            user_id = 666,
            aitype = 2,
            cls_type = cls, # 检测结果 0 未检测
            cls_name = name,
            imgpath = absolute_image_url,
            img_bbox = boxs, # 检测框
            result_time = current_time,
        )
        ailog.save()
        urls.append(absolute_image_url)
        names.append(name)
    return JsonResponse({'code':200,'path': urls,'name': names})

def deldata(request):
    data_skin.objects.all().delete()
    data_tumor.objects.all().delete()
    return JsonResponse({'code':200})

def user_information(request):
    # 只处理 POST 请求
    if request.method != 'POST':
        return JsonResponse({"code": 400, "msg": "请求方法错误"})

    # 数据格式转换，拿到前端传来的数据
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"code": 400, "msg": "无效的请求数据"})

    # 从数据中提取手机号和密码
    phone = data.get("tel")
    password = data.get("passwd")

    if not phone or not password:
        return JsonResponse({"code": 400, "msg": "缺少必要的字段"})

    # 进行数据库验证
    try:
        user_info = User.objects.get(phone=phone)  # 确保字段名称与模型一致
    except User.DoesNotExist:
        return JsonResponse({"code": 408, "msg": "用户不存在"})

    # 验证密码，注意：实际应用中应使用安全的密码处理机制
    if user_info.password == password:
        # user = {
        #     # Patient.objects.filter()
        #     "name": "小红",  # 可以替换为实际用户信息
        #     "tel": user_info.phone  # 确保字段名与数据库字段一致
        # }
        return JsonResponse({"code": 200, "data": 'success'})
    else:
        return JsonResponse({"code": 405, "msg": "密码错误"})

def upload_img(request):
    if request.method == 'POST':
        files = request.FILES.getlist('avatar')
        if not files:
            return JsonResponse({"code": 400, "msg": "没有接收到文件"})
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        ext = os.path.splitext(files[0].name)[1]  # 获取文件扩展名
        filename = f"{int(time.time()*1000)}_{random.randint(1000,9999)}{ext}"

        filepath = fs.save(filename, files[0])

        imgurl = f"{settings.HOSTS_DOMAIN}{settings.MEDIA_URL}/avatar/{filename}"  # 使用 MEDIA_URL
        return JsonResponse({"code": 200, "msg": "ok", "img": imgurl})

        return JsonResponse({"code": 400, "msg": "无效的请求方法"})

def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            phone = data.get('phone')
            password = data.get('password')
            if not phone or not password:
                return JsonResponse({"code": 401, "message": "手机号或密码不能为空"})
            user =User.objects.filter(phone=phone)
            if user.exists() :
                return JsonResponse({"code": 403, "message": "用户已存在"})

            User.objects.create(phone=phone, password=password)
            return JsonResponse({"code": 200, "message": "添加用户成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": "添加失败: " + str(e)})
    return JsonResponse({"code": 402, "message": "请求方法错误"})

def imgurl(request):

    # 接收客户端提交上来的图片
    imgfile = request.FILES.get("file")
    # 创建filesystemstorage对象并保存图片到static目录下
    fs = FileSystemStorage(location='static/avatar')
    filename = f"{int(time.time() * 100)}_{random.randint(0, 999)}_{imgfile.name}"
    fname = fs.save(filename, imgfile)


    # global img_url
    # img_url=imgfile.name
    # print(os.path.join(STATICFILES_DIRS[0], fname))

    return JsonResponse({"code": 200, "msg": fname})

def real_name(request):
    data = json.loads(request.body.decode('utf-8'))

    print(data)
    password = data.get('password')
    account =  data.get('account')

    # avator =request.FILES.get("avatar")
    avator="/static/avatar/" + data.get('img_name')
    name = data.get('name')
    gender =data.get('gender')
    age = data.get('age')
    Patient.objects.create(account=account,password=password,avator=avator,name=name,gender=gender,age=age)
    return JsonResponse({"code": 200, "message": "实名成功"})

def getInfo(request):
    import json
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    database=Patient.objects.filter(account=data.get('account'))
    print(database)
    host = "http://" + request.get_host()  # 获取主机名
    data_list = []
    for i in database:
        record = {
            "name": i.name,
            "gender": i.gender,
            "age": i.age,
            'avatar':host + i.avator,
        }
        data_list.append(record)
    return JsonResponse({"code": 200, "data": data_list})

def getAvatar(request):
    data = json.loads(request.body.decode('utf-8'))
    database=Patient.objects.filter(account=data.get('account'))
    host = "http://" + request.get_host()  # 获取主机名
    imgurl=''
    for i in database:
        imgurl=host + i.avator
        print(imgurl)
    return JsonResponse({"code": 200, "data": imgurl})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # 明确指定允许所有用户访问
def login_view(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        return Response({
            'code': 200,
            'message': 'Login successful',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': profile.is_admin
            }
        })
    else:
        return Response({
            'code': 401,
            'message': 'Invalid credentials'
        })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if User.objects.filter(username=username).exists():
        return Response({
            'code': 400,
            'message': 'Username already exists'
        })

    try:
        # 创建用户
        user = User.objects.create_user(username=username, password=password, email=email)


        print("created user:", user.username, user.password, user.email)

        # 使用 UserProfile.objects.create 方法创建用户资料
        UserProfile.objects.create(user=user, is_admin=False)

        return Response({
            'code': 200,
            'message': 'Registration successful'
        })
    except Exception as e:
        # 如果出现错误，返回详细信息
        print(f"Registration error: {str(e)}")
        return Response({
            'code': 500,
            'message': f'Registration failed: {str(e)}'
        })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detect_face(request):
    if 'image' not in request.FILES:
        return Response({
            'code': 400,
            'message': 'No image provided'
        })

    image_file = request.FILES['image']

    # 保存上传的图片
    img_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image_file.name)
    os.makedirs(os.path.dirname(img_path), exist_ok=True)

    with open(img_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)

    # 使用YOLOv5进行人脸检测
    results = model(img_path)

    # 提取检测结果
    detections = []
    for pred in results.xyxy[0]:  # 遍历每个检测结果
        x1, y1, x2, y2, conf, cls = pred.cpu().numpy()
        detections.append({
            'bbox': [float(x1), float(y1), float(x2), float(y2)],
            'confidence': float(conf)
        })

    return Response({
        'code': 200,
        'message': 'Detection successful',
        'results': detections
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_detection(request):
    if 'image' not in request.FILES:
        return Response({
            'code': 400,
            'message': 'No image provided'
        })

    image_file = request.FILES['image']
    results_json = request.POST.get('results', '[]')

    try:
        results = json.loads(results_json)
    except json.JSONDecodeError:
        return Response({
            'code': 400,
            'message': 'Invalid results data'
        })

    # 保存检测记录
    detection = FaceDetection.objects.create(
        user=request.user,
        image=image_file,
        face_count=len(results)
    )

    # 保存每个检测到的人脸
    for result in results:
        DetectedFace.objects.create(
            detection=detection,
            bbox=result['bbox'],
            confidence=result['confidence']
        )

    return Response({
        'code': 200,
        'message': 'Detection saved successfully'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detection_history(request):
    # 只有管理员可以查看所有历史记录
    if not request.user.profile.is_admin:
        return Response({
            'code': 403,
            'message': 'Permission denied'
        })

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    queryset = FaceDetection.objects.all().order_by('-created_at')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + timedelta(days=1)
        queryset = queryset.filter(created_at__lte=end_date)

    data = []
    for detection in queryset:
        data.append({
            'id': detection.id,
            'image_url': request.build_absolute_uri(detection.image.url),
            'face_count': detection.face_count,
            'created_at': detection.created_at.isoformat(),
            'user_name': detection.user.username
        })

    return Response({
        'code': 200,
        'data': data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detection_detail(request, pk):
    # 只有管理员可以查看详情
    if not request.user.profile.is_admin:
        return Response({
            'code': 403,
            'message': 'Permission denied'
        })

    try:
        detection = FaceDetection.objects.get(pk=pk)
    except FaceDetection.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'Detection not found'
        })

    faces = []
    for face in detection.faces.all():
        faces.append({
            'bbox': face.bbox,
            'confidence': face.confidence
        })

    data = {
        'id': detection.id,
        'image_url': request.build_absolute_uri(detection.image.url),
        'face_count': detection.face_count,
        'created_at': detection.created_at.isoformat(),
        'user_name': detection.user.username,
        'faces': faces
    }

    return Response({
        'code': 200,
        'data': data
    })

