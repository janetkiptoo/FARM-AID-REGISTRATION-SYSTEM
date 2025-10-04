from urllib import request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Farmer, AidApplication
from .forms import FarmerForm, AidApplicationForm
from .models import Farmer, AidApplication



applications = []  # temporary store (replace with DB model later)




# Farmer registration + Aid application
def apply_aid(request):
    if request.method == "POST":
        farmer_form = FarmerForm(request.POST)
        aid_form = AidApplicationForm(request.POST)

        if farmer_form.is_valid() and aid_form.is_valid():
            id_number = farmer_form.cleaned_data["id_number"]

            # Check if farmer already exists
            farmer, created = Farmer.objects.get_or_create(
                id_number=id_number,
                defaults=farmer_form.cleaned_data
            )

            # If farmer exists but we want to update their details
            if not created:
                for field, value in farmer_form.cleaned_data.items():
                    setattr(farmer, field, value)
                farmer.save()

            # Prevent duplicate aid requests (same farmer + same resource)
            resource = aid_form.cleaned_data["resources_needed"]
            if AidApplication.objects.filter(farmer=farmer, resources_needed=resource).exists():
                messages.error(request, f"You have already applied for {resource}.")
            else:
                aid_application = aid_form.save(commit=False)
                aid_application.farmer = farmer
                aid_application.save()
                messages.success(request, "Application submitted successfully!")

            return redirect("apply_aid")
    else:
        farmer_form = FarmerForm()
        aid_form = AidApplicationForm()

    return render(request, "core/apply_aid.html", {
        "farmer_form": farmer_form,
        "aid_form": aid_form
    })


# Farmer Dashboard (basic example)
def dashboard(request):
    farmers = Farmer.objects.all()
    applications = AidApplication.objects.all()
    return render(request, "core/dashboard.html", {
        "farmers": farmers,
        "applications": applications
    })

def status_view(request, id_number):
    # Look up farmer application by ID number
    application = get_object_or_404(FarmerApplication, id_number=id_number)
    
    return render(request, "core/status.html", {
        "application": application
    })

def index(request):
    farmer = None
    if request.user.is_authenticated:
        try:
           # Just show all farmers for now
         farmers = Farmer.objects.all()
         farmer = farmers.first()  # or however you want to select
        except Farmer.DoesNotExist:
            farmer = None
    return render(request, "core/index.html", {"farmer": farmer})



def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")

def status(request):
    return render(request, "core/status.html")


@login_required
def apply_aid(request):
    return render(request, "core/apply_aid.html")
