from rest_framework import permissions
from users.models import MANAGER


class IsAnnouncementOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.univercity.user == request.user


class CanAddAnnouncement(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.universities.exists() and request.user.user_role == MANAGER
