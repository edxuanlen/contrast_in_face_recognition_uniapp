from django.urls import path
from . import views

urlpatterns = [
    path("tmourname/", views.class_tumor_list, name="about"),
    path("tmour/", views.tmour_preds, name="about"),
    path("tmourdel/", views.tmourdelete, name="index"),
    path("del/", views.deldata, name="index"),
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
]
