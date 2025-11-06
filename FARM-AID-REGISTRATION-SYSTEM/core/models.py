from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


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


# ✅ Custom User model
class User(AbstractUser):
    is_officer = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# ✅ Farmer model
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
        ],
        blank=True,
        null=True
    )
    date_registered = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"

class AidItem(models.Model):
    AID_CHOICES = [
        ('fertilizer', 'Fertilizer'),
        ('seedlings', 'Seedlings'),
        ('pesticides', 'Pesticides'),
        ('animal_feed', 'Animal Feed'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, choices=AID_CHOICES)
    quantity_available = models.PositiveIntegerField(default=0)
    application_start = models.DateField()
    application_deadline = models.DateField()
    is_open_for_application = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()


class SubAidItem(models.Model):
    """Sub-items under each Aid category, e.g., DAP, CAN under Fertilizer"""
    aid_item = models.ForeignKey(AidItem, related_name='sub_items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity_available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.aid_item.get_name_display()})"

# ✅ AidApplication model
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
    aid_item = models.ForeignKey(AidItem, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # new application

            aid_item = AidItem.objects.filter(name=self.resources_needed).first()
            if aid_item:
                if aid_item.quantity_available > 0:
                    aid_item.quantity_available -= 1
                    aid_item.save()
                    self.aid_item = aid_item
                else:
                    raise ValueError(f"Sorry, {aid_item.get_name_display()} is out of stock.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.farmer.full_name} - {self.resources_needed}"


# ✅ ContactMessage model
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replied_messages"
    )
    replied_at = models.DateTimeField(null=True, blank=True)
    is_reply_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


# ✅ Notification model
class Notification(models.Model):
    RECIPIENT_CHOICES = [
        ("single", "Single Farmer"),
        ("all", "All Farmers"),
    ]

    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES, default="single")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_recipient_type_display()} - {self.phone_number or 'All'}"


# ✅ Farmer update form
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
