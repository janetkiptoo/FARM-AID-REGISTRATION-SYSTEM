from django.db import models

class Farmer(models.Model):
    full_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2)
    farming_type = models.CharField(max_length=50, choices=[
        ('crop', 'Crop Farming'),
        ('livestock', 'Livestock Farming'),
        ('mixed', 'Mixed Farming'),
    ])

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"


class AidApplication(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="applications")
    resources_needed = models.CharField(max_length=200, choices=[
        ('seedlings', 'Seedlings'),
        ('fertilizers', 'Fertilizers'),
        ('pesticides', 'Pesticides'),
        ('livestock_vaccines', 'Livestock Vaccines'),
        ('equipment', 'Farming Equipment'),
        ('financial_support', 'Financial Support'),
    ])
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('farmer', 'resources_needed')  # prevent duplicate same-aid requests

    def __str__(self):
        return f"{self.farmer.full_name} - {self.resources_needed}"



