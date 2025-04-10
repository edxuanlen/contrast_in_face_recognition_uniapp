from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    自定义权限类，检查用户是否是管理员
    """
    def has_permission(self, request, view):
        try:
            return bool(request.user and request.user.is_authenticated and request.user.profile.is_admin)
        except:
            return False
