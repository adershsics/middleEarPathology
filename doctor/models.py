from django.db import models
from django.core.validators import validate_email,validate_slug
from django.contrib.auth.password_validation import validate_password 
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.
class doctor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    mobile_number = PhoneNumberField(unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True, validators=[validate_email])
    hospital_name = models.CharField(max_length=100)
    doctor_id_number = models.CharField(max_length=20, unique=True, validators=[validate_slug])
    def __str__(self):
        return self.name    
