from rest_framework.permissions import BasePermission


class CanCreateDevice(BasePermission):
    """
    Permission to allow only superusers and users in the 'device_creators' group
    to create devices.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        # Superuser can always create
        if request.user.is_superuser:
            return True

        # Check if user is in the 'device_creators' group
        return request.user.groups.filter(name="device_creators").exists()
