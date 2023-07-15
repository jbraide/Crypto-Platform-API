from django.contrib import admin
from .models import KYC, UserProfile

@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['profile', 'proof_of_address', ]
