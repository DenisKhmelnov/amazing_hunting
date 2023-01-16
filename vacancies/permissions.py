from rest_framework.permissions import BasePermission

from authentication.models import User


class VacancyCreatePermission(BasePermission):
    message = "Forbidden creating vacancy for non HR user"

    def has_permission(self, request, view):
        if request.user.role == User.HR:
            return True
        else:
            return False