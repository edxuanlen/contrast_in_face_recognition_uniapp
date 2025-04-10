from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from server.settings import STATICFILES_DIRS
# from app import pred
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
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import cv2
import numpy as np
import torch
from PIL import Image
import platform
from pathlib import Path
import face_recognition
import pickle
import io
from app.permissions import IsAdminUser

# 在加载模型之前添加这段代码
if platform.system() == 'Windows':
    # 在Windows上修复PosixPath问题
    import pathlib
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

# 然后再加载模型
model = torch.hub.load('ultralytics/yolov5', 'custom', path='app/yolov5/weights/face_detection.pt', force_reload=False)
model.conf = 0.5  # 设置置信度阈值


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
            user = User.objects.filter(phone=phone)
            if user.exists():
                return JsonResponse({"code": 403, "message": "用户已存在"})

            # 创建新用户
            new_user = User.objects.create(phone=phone, password=password)

            # 检查是否为第一个用户，如果是则赋予管理员权限
            if User.objects.count() == 1:
                # 为该用户创建UserProfile并设置is_admin为True
                UserProfile.objects.create(user=new_user, is_admin=True)
            else:
                # 为普通用户创建UserProfile
                UserProfile.objects.create(user=new_user, is_admin=False)

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
def add_face_to_library(request):
    if 'image' not in request.FILES:
        return Response({
            'code': 400,
            'message': 'No image provided'
        })

    image_file = request.FILES['image']
    name = request.POST.get('name', '')

    if not name:
        return Response({
            'code': 400,
            'message': 'Name is required'
        })

    # 加载图像
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        return Response({
            'code': 400,
            'message': 'No face detected in the image'
        })

    if len(face_locations) > 1:
        return Response({
            'code': 400,
            'message': 'Multiple faces detected, please provide an image with a single face'
        })

    # 提取人脸特征
    face_encoding = face_recognition.face_encodings(image, face_locations)[0]

    # 将特征向量转换为二进制
    face_encoding_binary = pickle.dumps(face_encoding)

    # 保存到数据库
    library_entry = FaceLibrary.objects.create(
        user=request.user,
        name=name,
        image=image_file,
        face_encoding=face_encoding_binary
    )

    return Response({
        'code': 200,
        'message': 'Face added to library successfully',
        'id': library_entry.id
    })

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_face_library(request):
    # 获取用户的人脸库列表
    faces = FaceLibrary.objects.filter(user=request.user).order_by('-created_at')

    data = []
    for face in faces:
        data.append({
            'id': face.id,
            'name': face.name,
            'image_url': request.build_absolute_uri(face.image.url),
            'created_at': face.created_at.isoformat()
        })

    return Response({
        'code': 200,
        'data': data
    })

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_face_from_library(request, pk):
    try:
        face = FaceLibrary.objects.get(pk=pk, user=request.user)
    except FaceLibrary.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'Face not found in library'
        })

    face.delete()

    return Response({
        'code': 200,
        'message': 'Face removed from library successfully'
    })

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_face_library(request, face_id):
    try:
        face = FaceLibrary.objects.get(pk=face_id, user=request.user)
    except FaceLibrary.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'Face not found in library'
        })

    face.name = request.data.get('name')
    face.save()

    return Response({
        'code': 200,
        'message': 'Face updated successfully'
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

        # 构造基本检测结果
        detection = {
            'bbox': [float(x1), float(y1), float(x2), float(y2)],
            'confidence': float(conf),
            'recognition': {
                'name': 'Unknown',
                'similarity': 0.0
            }
        }

        # 如果检测置信度超过阈值，进行人脸识别
        if float(conf) > 0.5:
            # 从原始图像中裁剪出人脸区域
            image = cv2.imread(img_path)
            face_img = image[int(y1):int(y2), int(x1):int(x2)]

            # 将OpenCV格式转换为face_recognition需要的格式
            face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

            # 识别人脸
            face_locations = face_recognition.face_locations(face_img_rgb)

            if face_locations:
                face_encodings = face_recognition.face_encodings(face_img_rgb, face_locations)

                if face_encodings:
                    # 获取人脸库中的所有人脸
                    face_library = FaceLibrary.objects.all()

                    best_match = {
                        'name': 'Unknown',
                        'similarity': 0.0,
                        'face_id': None
                    }

                    # 与库中的人脸进行比较
                    for lib_face in face_library:
                        try:
                            # 转换二进制为numpy数组
                            lib_face_encoding = pickle.loads(lib_face.face_encoding)

                            # 计算距离
                            face_distance = face_recognition.face_distance([lib_face_encoding], face_encodings[0])[0]

                            # 将距离转换为相似度
                            similarity = 1 - face_distance

                            # 如果相似度更高，更新最佳匹配
                            if similarity > 0.5 and similarity > best_match['similarity']:
                                best_match = {
                                    'name': lib_face.name,
                                    'similarity': float(similarity),
                                    'face_id': lib_face.id
                                }
                        except Exception as e:
                            print(f"Error comparing face: {str(e)}")
                            continue

                    detection['recognition'] = best_match

        detections.append(detection)

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
        detected_face = DetectedFace.objects.create(
            detection=detection,
            bbox=result['bbox'],
            confidence=result['confidence']
        )

        # 如果有识别结果，且相似度超过0.5
        if 'recognition' in result and result['recognition']['similarity'] > 0.5:
            recognition = result['recognition']

            try:
                face_library = FaceLibrary.objects.get(id=recognition.get('face_id'))

                # 保存识别结果
                RecognizedFace.objects.create(
                    detection=detected_face,
                    face_library=face_library,
                    similarity=recognition['similarity']
                )
            except FaceLibrary.DoesNotExist:
                # 如果找不到对应的库中人脸，跳过保存识别结果
                pass

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
    # 非管理员也可以查看自己的检测记录
    try:
        if request.user.profile.is_admin:
            detection = FaceDetection.objects.get(pk=pk)
        else:
            detection = FaceDetection.objects.get(pk=pk, user=request.user)
    except FaceDetection.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'Detection not found'
        })

    faces = []
    for face in detection.faces.all():
        face_data = {
            'bbox': face.bbox,
            'confidence': face.confidence,
            'recognition': {
                'name': 'Unknown',
                'similarity': 0.0
            }
        }

        # 获取人脸识别结果
        try:
            recognized_face = face.recognitions.first()
            if recognized_face:
                face_data['recognition'] = {
                    'name': recognized_face.face_library.name,
                    'similarity': recognized_face.similarity
                }
        except:
            pass

        faces.append(face_data)

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_directory_to_library(request):
    # 验证用户是否为管理员
    if not request.user.profile.is_admin:
        return Response({
            'code': 403,
            'message': 'Permission denied. Only admin can perform this operation.'
        })

    # 获取路径和默认名称前缀
    directory_path = request.data.get('directory_path')
    # directory_path = '/media/faces/'
    name_prefix = request.data.get('name_prefix', 'Person')

    if not directory_path:
        return Response({
            'code': 400,
            'message': 'Directory path is required'
        })

    # 检查路径是否存在
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return Response({
            'code': 400,
            'message': 'Invalid directory path'
        })

    # 定义接受的图片扩展名
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

    # 收集结果统计
    stats = {
        'total_images': 0,
        'processed': 0,
        'added': 0,
        'skipped_no_face': 0,
        'skipped_multiple_faces': 0,
        'skipped_existing': 0,
        'errors': 0
    }

    # 用于检查图片是否已经存在于库中的函数
    def is_face_in_library(face_encoding):
        # 获取所有已有的人脸编码
        all_faces = FaceLibrary.objects.all()

        for lib_face in all_faces:
            try:
                # 解码库中的人脸编码
                lib_encoding = pickle.loads(lib_face.face_encoding)

                # 计算相似度
                distance = face_recognition.face_distance([lib_encoding], face_encoding)[0]
                similarity = 1 - distance

                # 如果相似度很高，认为是同一个人脸
                if similarity > 0.6:
                    return True, lib_face.name
            except:
                continue

        return False, None

    # 处理结果列表
    results = []

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # 检查是否是文件且扩展名匹配
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in valid_extensions:
            stats['total_images'] += 1
            result_item = {
                'filename': filename,
                'status': 'processed'
            }

            try:
                # 读取图像文件
                image = face_recognition.load_image_file(file_path)
                face_locations = face_recognition.face_locations(image)

                if not face_locations:
                    result_item['status'] = 'skipped'
                    result_item['reason'] = 'No face detected'
                    stats['skipped_no_face'] += 1
                elif len(face_locations) > 1:
                    result_item['status'] = 'skipped'
                    result_item['reason'] = 'Multiple faces detected'
                    stats['skipped_multiple_faces'] += 1
                else:
                    # 提取人脸特征
                    face_encoding = face_recognition.face_encodings(image, face_locations)[0]

                    # 检查是否已存在于库中
                    exists, existing_name = is_face_in_library(face_encoding)

                    if exists:
                        result_item['status'] = 'skipped'
                        result_item['reason'] = f'Face already exists as {existing_name}'
                        stats['skipped_existing'] += 1
                    else:
                        # 创建一个唯一的名称
                        face_name = f"{name_prefix}_{stats['added'] + 1}"

                        # 转换特征为二进制
                        face_encoding_binary = pickle.dumps(face_encoding)

                        # 打开文件并创建类似于InMemoryUploadedFile的文件对象
                        with open(file_path, 'rb') as f:
                            file_content = f.read()

                        # 创建InMemoryUploadedFile对象
                        from django.core.files.uploadedfile import InMemoryUploadedFile
                        import io

                        file_obj = InMemoryUploadedFile(
                            io.BytesIO(file_content),
                            'image',
                            os.path.basename(file_path),
                            'image/jpeg',
                            len(file_content),
                            None
                        )

                        # 保存到数据库
                        FaceLibrary.objects.create(
                            user=request.user,
                            name=face_name,
                            image=file_obj,
                            face_encoding=face_encoding_binary
                        )

                        result_item['status'] = 'added'
                        result_item['name'] = face_name
                        stats['added'] += 1

                stats['processed'] += 1
            except Exception as e:
                result_item['status'] = 'error'
                result_item['reason'] = str(e)
                stats['errors'] += 1

            results.append(result_item)

    return Response({
        'code': 200,
        'message': 'Directory scan completed',
        'stats': stats,
        'results': results
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_detection_history(request, pk):
    # 只有管理员可以删除历史记录
    if not request.user.profile.is_admin:
        return Response({
            'code': 403,
            'message': 'Permission denied. Only admin can delete history records.'
        })

    try:
        # 获取检测记录
        detection = FaceDetection.objects.get(pk=pk)

        # 删除相关联的检测到的人脸和识别结果
        for face in detection.faces.all():
            face.recognitions.all().delete()
            face.delete()

        # 删除检测记录本身
        detection.delete()

        return Response({
            'code': 200,
            'message': 'History record deleted successfully'
        })
    except FaceDetection.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'History record not found'
        })
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'Failed to delete history record: {str(e)}'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_users(request):
    """获取所有用户列表"""
    users = User.objects.all()
    data = []

    for user in users:
        try:
            profile = user.profile
            is_admin = profile.is_admin
        except UserProfile.DoesNotExist:
            is_admin = False

        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': is_admin,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        })

    return Response({
        'code': 200,
        'data': data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggle_admin_status(request, user_id):
    """切换用户的管理员状态"""
    try:
        target_user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=target_user)

        # 切换管理员状态
        profile.is_admin = not profile.is_admin
        profile.save()

        return Response({
            'code': 200,
            'message': f'Successfully {"granted" if profile.is_admin else "revoked"} admin privileges',
            'is_admin': profile.is_admin
        })
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'User not found'
        })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, user_id):
    """删除用户"""
    try:
        user = User.objects.get(id=user_id)

        # 防止删除自己
        if user.id == request.user.id:
            return Response({
                'code': 400,
                'message': 'Cannot delete your own account'
            })

        user.delete()
        return Response({
            'code': 200,
            'message': 'User deleted successfully'
        })
    except User.DoesNotExist:
        return Response({
            'code': 404,
            'message': 'User not found'
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """管理员创建新用户"""
    # 检查当前用户是否是管理员
    try:
        if not request.user.profile.is_admin:
            return Response({
                'code': 403,
                'message': 'Permission denied. Only admin can create users.'
            })
    except:
        return Response({
            'code': 403,
            'message': 'Permission denied.'
        })

    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    is_admin = data.get('is_admin', False)

    if not username or not password:
        return Response({
            'code': 400,
            'message': 'Username and password are required'
        })

    if User.objects.filter(username=username).exists():
        return Response({
            'code': 400,
            'message': 'Username already exists'
        })

    try:
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # 创建用户资料
        UserProfile.objects.create(
            user=user,
            is_admin=is_admin
        )

        return Response({
            'code': 200,
            'message': 'User created successfully',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': is_admin
            }
        })
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'Failed to create user: {str(e)}'
        })

