from django.urls import path
from . import views

urlpatterns = [
    path("userin/", views.user_information, name="index"),
    path("upimg/", views.upload_img, name="index"),
    path("register/", views.register, name="index"),
    path("realname/", views.real_name, name="index"),
    path("imgurl/", views.imgurl, name="index"),
    path("getinfo/", views.getInfo, name="index"),
    path("getavatar/", views.getAvatar, name="index"),
    path('api/login/', views.login_view, name='login'),
    path('api/register/', views.register_view, name='register'),
    path('api/detect_face/', views.detect_face, name='detect_face'),
    path('api/save_detection/', views.save_detection, name='save_detection'),
    path('api/detection_history/', views.detection_history, name='detection_history'),
    path('api/detection_detail/<int:pk>/', views.detection_detail, name='detection_detail'),
    path('api/detection_history/<int:pk>/', views.delete_detection_history, name='delete_detection_history'),
    path('api/face_library/add/', views.add_face_to_library, name='add_face_to_library'),
    path('api/face_library/list/', views.list_face_library, name='list_face_library'),
    path('api/face_library/update/<int:face_id>/', views.update_face_library, name='update_face_library'),
    path('api/face_library/delete/<int:pk>/', views.delete_face_from_library, name='delete_face_from_library'),
    path('api/face_library/scan_directory/', views.scan_directory_to_library, name='scan_directory_to_library'),
    path('api/admin/users/create/', views.create_user, name='create_user'),
    path('api/admin/users/', views.list_users, name='list_users'),
    path('api/admin/users/<int:user_id>/toggle-admin/', views.toggle_admin_status, name='toggle_admin_status'),
    path('api/admin/users/<int:user_id>/', views.delete_user, name='delete_user'),
]
