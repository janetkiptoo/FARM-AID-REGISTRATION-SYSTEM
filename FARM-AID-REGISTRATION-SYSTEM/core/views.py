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
        aid_form = AidApplicationForm(request.POST)
        id_number = request.POST.get("id_number")

        # Try to get or create the farmer manually to avoid form uniqueness validation
        farmer = None
        if id_number:
            try:
                farmer = Farmer.objects.get(id_number=id_number)
                # Update farmer info with new data
                farmer.full_name = request.POST.get("full_name", farmer.full_name)
                farmer.phone_number = request.POST.get("phone_number", farmer.phone_number)
                farmer.county = request.POST.get("county", farmer.county)
                farmer.sub_county = request.POST.get("sub_county", farmer.sub_county)
                farmer.ward = request.POST.get("ward", farmer.ward)
                if request.user.is_authenticated:
                    farmer.user = request.user
                farmer.save()
            except Farmer.DoesNotExist:
                farmer = Farmer.objects.create(
                    id_number=id_number,
                    full_name=request.POST.get("full_name"),
                    phone_number=request.POST.get("phone_number"),
                    county=request.POST.get("county"),
                    sub_county=request.POST.get("sub_county"),
                    ward=request.POST.get("ward"),
                    farm_size=request.POST.get("farm_size") or 0,
                    farming_type=request.POST.get("farming_type") or "mixed",
                    user=request.user if request.user.is_authenticated else None
                )

        if aid_form.is_valid() and farmer:
            resource = aid_form.cleaned_data["resources_needed"]

            # Prevent duplicate active applications
            existing_application = AidApplication.objects.filter(
                farmer=farmer,
                resources_needed=resource
            ).exclude(status="rejected").exists()

            if existing_application:
                messages.error(
                    request,
                    f"You already have an active application for {resource}. Please wait for it to be processed."
                )
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
        "farmer_form": FarmerForm(),
        "aid_form": AidApplicationForm(),
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
def delete_application(request, app_id):
    application = get_object_or_404(AidApplication, id=app_id, farmer__user=request.user)
    if application.status == 'pending':
        application.delete()
        messages.success(request, "Your application has been deleted successfully.")
    else:
        messages.error(request, "You can only delete applications that are still pending.")
    return redirect('dashboard')



def status_view(request, id_number):
    farmer = get_object_or_404(Farmer, id_number=id_number)
    applications = AidApplication.objects.filter(farmer=farmer)

    return render(request, "core/status.html", {
        "farmer": farmer,
        "applications": applications
    })

@login_required
def reapply_application(request, app_id):
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404

    application = get_object_or_404(AidApplication, id=app_id, farmer__user=request.user)
    
    if application.status == 'rejected':
        messages.info(request, "You can now reapply for aid. Please fill out the form again.")
        return redirect('apply_aid')  # make sure this name matches your application form URL name
    else:
        messages.error(request, "You can only reapply for rejected applications.")
        return redirect('application_status')




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





