

## how to run

1. data migrate
```
python manage.py makemigrations
python manage.py migrate
```
2. run server
```
python manage.py runserver 0.0.0.0:8000
```


以下是根据您的模型生成的表格：

### 表 Patient 表

| 字段名称 | 数据类型 | 长度 | 字段含义 | 约束 |
|---------|---------|-----|---------|-----|
| id | INT | - | 用户ID | 主键、非空、自增 |
| account | VARCHAR | 32 | 账号 | 非空 |
| password | VARCHAR | 64 | 密码 | 非空 |
| avator | VARCHAR | 255 | 头像URL | 允许为空 |
| is_admin | TINYINT | 1 | 是否管理员 | 非空 |

### 表 FaceDetection 表

| 字段名称 | 数据类型 | 长度 | 字段含义 | 约束 |
|---------|---------|-----|---------|-----|
| id | INT | - | 检测ID | 主键、非空、自增 |
| user_id | INT | - | 关联用户 | 外键、非空 |
| image | VARCHAR | 255 | 图像路径 | 非空 |
| face_count | INT | - | 人脸数量 | 非空 |
| created_at | DATETIME | - | 创建时间 | 非空 |

### 表 DetectedFace 表

| 字段名称 | 数据类型 | 长度 | 字段含义 | 约束 |
|---------|---------|-----|---------|-----|
| id | INT | - | 人脸ID | 主键、非空、自增 |
| detection_id | INT | - | 关联检测 | 外键、非空 |
| bbox | JSON | - | 边界框坐标 | 非空 |
| confidence | FLOAT | - | 置信度 | 非空 |

### 表 UserProfile 表

| 字段名称 | 数据类型 | 长度 | 字段含义 | 约束 |
|---------|---------|-----|---------|-----|
| id | INT | - | 配置ID | 主键、非空、自增 |
| user_id | INT | - | 关联用户 | 外键、非空 |
| is_admin | TINYINT | 1 | 是否管理员 | 非空 |
