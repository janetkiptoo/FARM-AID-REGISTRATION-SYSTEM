from django import forms
from .models import Farmer, AidApplication
from .models import Notification
from .models import Farmer
from .models import AidItem
from .models import AidApplication, AidItem, SubAidItem
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
        fields = ["aid_item", "sub_aid_item", "quantity_requested"]
        widgets = {
            'aid_item': forms.Select(attrs={'class': 'form-control', 'id': 'aid-item-select'}),
            'sub_aid_item': forms.Select(attrs={'class': 'form-control', 'id': 'sub-aid-item-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_aid_item'].queryset = SubAidItem.objects.none()

        if 'aid_item' in self.data:
            try:
                aid_item_id = int(self.data.get('aid_item'))
                self.fields['sub_aid_item'].queryset = SubAidItem.objects.filter(aid_item_id=aid_item_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.aid_item:
            self.fields['sub_aid_item'].queryset = self.instance.aid_item.sub_items.all()


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


    
class AidItemForm(forms.ModelForm):
    class Meta:
        model = AidItem
        fields = ["quantity_available", "application_start", "application_deadline"]
        widgets = {
            "quantity_available": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "application_start": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "application_deadline": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }