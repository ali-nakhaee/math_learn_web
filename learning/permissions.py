from rest_framework.permissions import BasePermission

class TeacherhoodPermission(BasePermission):
    message = "Access Denied!. You must be a teacher."

    def has_permission(self, request, view):
        if request.user.role == 'TEACHER':
            return True
        return False
    