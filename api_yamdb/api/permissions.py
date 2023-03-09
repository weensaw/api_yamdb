from rest_framework import permissions


#class IsOwnerOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
#    def has_object_permission(self, request, view, obj):
#        if request.method in permissions.SAFE_METHODS:
#            return True
#        if request.user.is_authenticated:
#            if request.user == obj.author:
#                return True
#            elif request.user.role in ['moderator', 'admin']:
#                return True
#            else:
#                return False
#        return False


#class IsAdminOrReadOnly(permissions.BasePermission):
#   def has_permission(self, request, view):
#        if request.method in permissions.SAFE_METHODS:
#           return True
#        if request.user.is_authenticated:
#            if request.user.role in ['admin', 'moderator']:
#                return True
#            else:
#                return False
#        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        return False


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in ['user', ]:
                return True
        return False


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_staff


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role in ['moderator', ]:
                return True
        return False


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.author == request.user
        else:
            return False
