from rest_framework.permissions import BasePermission


class IsNoticeUser(BasePermission):
    """
    Allows access only to admin users for notice post.
    """

    def has_permission(self, request, view):

        return bool(request.user and request.user.user_type in ['DEPARTMENT', 'SOCIETY'])
