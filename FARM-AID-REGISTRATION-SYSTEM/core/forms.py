from django import forms
from .models import Farmer, AidApplication
from .models import Notification
from .models import Farmer
class NotificationForm(forms.Form):
    ...



class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = [
            "full_name",
            "id_number",
            "phone_number",
            "email",
            "county",
            "sub_county",
            "ward",
            "farm_size",
            "farming_type",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "id_number": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "county": forms.TextInput(attrs={"class": "form-control"}),
            "sub_county": forms.TextInput(attrs={"class": "form-control"}),
            "ward": forms.TextInput(attrs={"class": "form-control"}),
            "farm_size": forms.NumberInput(attrs={"class": "form-control"}),
            "farming_type": forms.Select(attrs={"class": "form-control"}),
        }


class AidApplicationForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["resources_needed"]
        widgets = {
            "resources_needed": forms.Select(attrs={"class": "form-control"}),
        }



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
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "county": forms.TextInput(attrs={"class": "form-control"}),
            "sub_county": forms.TextInput(attrs={"class": "form-control"}),
            "ward": forms.TextInput(attrs={"class": "form-control"}),
            "farm_size": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
                "farming_type": forms.Select(attrs={"class": "form-control"}),
            }
    
    
class NotificationForm(forms.Form):
    RECIPIENT_CHOICES = [
        ('single', 'Single Farmer'),
        ('all', 'All Farmers'),
    ]

    recipient_type = forms.ChoiceField(choices=RECIPIENT_CHOICES, label="Send To")
    phone_number = forms.CharField(max_length=15, required=False, label="Phone Number (for single)")
    message = forms.CharField(widget=forms.Textarea, label="Message")