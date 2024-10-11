from rest_framework.permissions import BasePermission

ADMIN_GROUP_NAME = 'admin'
PLAYER_GROUP_NAME = 'player'


def has_permission(perm):
    class HasPermission(BasePermission):
        """
        Custom permission to check if the user has the custom permission.
        """

        def has_permission(self, request, view):
            return request.user.has_perm(perm=perm)

        def __str__(self):
            return f"HasPermission<{perm}>"

    return HasPermission
