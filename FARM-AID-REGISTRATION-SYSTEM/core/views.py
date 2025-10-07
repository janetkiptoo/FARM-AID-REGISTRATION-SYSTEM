from urllib import request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AidApplication, Farmer
from .forms import FarmerForm, AidApplicationForm

import json



applications = []  # temporary store (replace with DB model later)




# Farmer registration + Aid application
def apply_aid(request):
    if request.method == "POST":
        farmer_form = FarmerForm(request.POST)
        aid_form = AidApplicationForm(request.POST)

        if farmer_form.is_valid() and aid_form.is_valid():
            id_number = farmer_form.cleaned_data["id_number"]

            # Check if farmer exists or create new
            farmer, created = Farmer.objects.get_or_create(
                id_number=id_number,
                defaults=farmer_form.cleaned_data
            )

            # ✅ Link farmer to logged-in user if not already linked
            if request.user.is_authenticated:
                farmer.user = request.user

            # ✅ Update farmer info if already exists
            for field, value in farmer_form.cleaned_data.items():
                setattr(farmer, field, value)
            farmer.save()

            # ✅ Prevent duplicate applications
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



def dashboard(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
        applications = AidApplication.objects.filter(farmer=farmer)
    except Farmer.DoesNotExist:
        farmer = None
        applications = None

    return render(request, "core/dashboard.html", {
        "farmer": farmer,
        "applications": applications,
    })

@login_required
def withdraw_application(request, app_id):
    farmer = get_object_or_404(Farmer, user=request.user)
    application = get_object_or_404(AidApplication, id=app_id, farmer=farmer)

    if application.status == 'pending':
        application.delete()
        messages.success(request, "Your application has been successfully withdrawn.")
    else:
        messages.error(request, "You can only withdraw pending applications.")

    return redirect('dashboard')


def status_view(request, id_number):
    farmer = get_object_or_404(Farmer, id_number=id_number)
    applications = AidApplication.objects.filter(farmer=farmer)

    return render(request, "core/status.html", {
        "farmer": farmer,
        "applications": applications
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

# Removed duplicate withdraw_application function



def logout_view(request):
    logout(request)
    return redirect("login")





