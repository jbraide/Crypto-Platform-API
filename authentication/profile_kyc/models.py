from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    home_address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=100)
    
class KYC(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    proof_of_address = models.FileField(upload_to='documents/proof-of-address/')
    identification_documents = models.FileField(upload_to='documents/identification/')
    document_type = models.CharField(max_length=100, default='')
    is_verified = models.BooleanField(default=False)