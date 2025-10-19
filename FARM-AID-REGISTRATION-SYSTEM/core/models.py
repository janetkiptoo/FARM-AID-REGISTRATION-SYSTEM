from django.db import models

from django import forms
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# County coordinates (approximate centers)
COUNTY_COORDS = {
    "Uasin Gishu": (0.5143, 35.2698),
    "Nakuru": (-0.3031, 36.0800),
    "Kericho": (-0.3670, 35.2831),
    "Bungoma": (0.5631, 34.5600),
    "Kisumu": (-0.0917, 34.7680),
    "Elgeyo Marakwet": (0.8520, 35.5135),
    "Nandi": (0.1742, 35.0675),
    "Kisii": (-0.6817, 34.7667),
}

class Farmer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2)
    farming_type = models.CharField(
        max_length=50,
        choices=[
            ('crop', 'Crop Farming'),
            ('livestock', 'Livestock Farming'),
            ('mixed', 'Mixed Farming'),
            
        ], blank=True,
    null=True
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class AidApplication(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="applications")
    resources_needed = models.CharField(
        max_length=200,
        choices=[
            ('seedlings', 'Seedlings'),
            ('fertilizers', 'Fertilizers'),
            ('pesticides', 'Pesticides'),
            ('livestock_vaccines', 'Livestock Vaccines'),
            ('equipment', 'Farming Equipment'),
            ('financial_support', 'Financial Support'),
        ]
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.full_name} - {self.resources_needed}"



class FarmerUpdateForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = [
            "full_name",
            "phone_number",
            "email",
            "county",
            "sub_county",
            "ward",
            "farm_size",
            "farming_type",
        ]
        widgets = {
            "farming_type": forms.Select(attrs={"class": "form-control"}),
            "farm_size": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
        }

class Notification(models.Model):
    message = models.TextField()
    sent_to_all = models.BooleanField(default=False)
    recipients = models.ManyToManyField(Farmer, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification ({'All Farmers' if self.sent_to_all else 'Selected Farmers'})"

class User(AbstractUser):
   
 is_officer = models.BooleanField(default=False)

def __str__(self):
        return self.username