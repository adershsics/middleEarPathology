from django.contrib.auth.backends import ModelBackend
from .models import doctor

class MobileNumberBackend(ModelBackend):
    def authenticate(self, request, mobile_number=None, password=None, **kwargs):
        try:
            user = doctor.objects.get(mobile_number=mobile_number)
            if user.password==password:
                return user
        except doctor.DoesNotExist:
            return None
