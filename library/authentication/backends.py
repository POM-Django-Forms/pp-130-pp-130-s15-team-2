from django.contrib.auth.backends import ModelBackend
from authentication.models import CustomUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None