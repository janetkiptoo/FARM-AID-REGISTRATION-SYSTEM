from django import forms
from .models import Farmer, AidApplication

class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = [
            "full_name", "id_number", "phone_number", "email",
            "county", "sub_county", "ward", "farm_size", "farming_type"
        ]


class AidApplicationForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["resources_needed"]
