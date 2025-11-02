from urllib import request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AidApplication, Farmer
from .forms import FarmerForm, AidApplicationForm
from django.contrib import messages
from .models import ContactMessage
from .forms import FarmerUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .sms_utils import send_sms_notification
from .models import Notification
from .forms import NotificationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F

import africastalking

# use africastalking SDK's SMS client (AfricasTalkingGateway import removed)

username = "sandbox"
api_key = "atsk_5b254d369598cb7309f0e80d7faed886f687a79ae551d0cf2d6a0d517fd28a46a4ad4c47"
africastalking.initialize(username, api_key)
sms = africastalking.SMS

import json



applications = []  # temporary store (replace with DB model later)




# Farmer registration + Aid application
@login_required
def apply_aid(request):
    """
    Combined Farmer registration/update + Aid application view.
    """
    # Try to get the farmer profile for the logged-in user
    farmer = Farmer.objects.filter(user=request.user).first()

    if request.method == "POST":
        farmer_form = FarmerForm(request.POST, instance=farmer)
        aid_form = AidApplicationForm(request.POST)

        # Save or update farmer profile
        if farmer_form.is_valid():
            farmer = farmer_form.save(commit=False)
            farmer.user = request.user
            farmer.save()
            messages.success(request, "Farmer profile saved successfully ✅")
        else:
            messages.error(request, "Please correct the farmer info errors.")

        # Save aid application if farmer exists
        if farmer and aid_form.is_valid():
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
                messages.success(request, "Aid application submitted successfully ✅")

            return redirect("dashboard")  # after submission, go to dashboard

    else:
        farmer_form = FarmerForm(instance=farmer)
        aid_form = AidApplicationForm()

    return render(
        request,
        "core/apply_aid.html",
        {"farmer_form": farmer_form, "aid_form": aid_form, "farmer": farmer}
    )

def notify_farmer(aid_application, message):
    farmer = aid_application.farmer
    phone = farmer.phone_number  # Make sure Farmer model has this field

    # Save to DB
    notif = Notification.objects.create(farmer=farmer, message=message)

    # Send SMS
    sent = send_sms_notification(phone, message)
    if sent:
        notif.status = 'sent'
        notif.save()









@login_required
def dashboard(request):
    farmer = Farmer.objects.filter(user=request.user).first()
    if not farmer:
        messages.error(
            request, 
            "No farmer profile found for your account. Please register as a farmer first."
        )
        return redirect("apply_aid")  # updated redirect

    applications = AidApplication.objects.filter(farmer=farmer)

    # Compute summary stats safely
    total = applications.count()
    approved = applications.filter(status="approved").count()
    pending = applications.filter(status="pending").count()
    rejected = applications.filter(status="rejected").count()

    context = {
        "farmer": farmer,
        "applications": applications,
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
    }
    return render(request, "core/dashboard.html", context)


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

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        # Basic validation (optional but recommended)
        if not name or not email or not message_text:
            messages.error(request, "Please fill in all fields.")
            return redirect('contact')

        # Save message to the database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message_text
        )

        messages.success(request, "Your message has been received! We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'core/contact.html')




@login_required
def profile_update(request):
    farmer = Farmer.objects.filter(user=request.user).first()
    if not farmer:
        messages.error(request, "No farmer profile found. Please register as a farmer first.")
        return redirect("apply_aid")  # updated redirect

    if request.method == "POST":
        form = FarmerUpdateForm(request.POST, instance=farmer)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully ✅")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FarmerUpdateForm(instance=farmer)

    return render(request, "core/profile_update.html", {"form": form, "farmer": farmer})
def logout_view(request):
    logout(request)
    return redirect("login")


def registered_farmers(request):
    farmers = Farmer.objects.annotate(application_date=F('aidapplication__date_applied'))
    return render(request, 'officer/farmers.html', {'farmers': farmers})
    return render(request, 'officer/farmers.html', {'farmers': farmers})





def farmers_map(request):
    farmers = Farmer.objects.values("full_name", "county", "latitude", "longitude")
    return render(request, "core/farmers_map.html", {"farmers": list(farmers)})


def farmers_map_data(request):
    farmers = Farmer.objects.all()
    data = [
        {
            "name": farmer.full_name,
            "county": farmer.county,
            "latitude": farmer.latitude,
            "longitude": farmer.longitude,
            "farm_size": farmer.farm_size,
        }
        for farmer in farmers
        if farmer.latitude and farmer.longitude
    ]
    return JsonResponse(data, safe=False)






def send_sms_notification(recipients, message):
    try:
        response = sms.send(message, recipients)
        print("✅ SMS sent:", response)
        return response
    except Exception as e:
        print("❌ SMS error:", e)
        return None

def format_phone_number(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+254" + phone[1:]
    elif phone.startswith("7"):
        phone = "+254" + phone
    elif not phone.startswith("+"):
        phone = "+254" + phone
    return phone

def officer_notifications(request):
    notifications = Notification.objects.all().order_by("-date_sent")[:10]

    if request.method == "POST":
        recipient_type = request.POST.get("recipient_type")
        phone_number = request.POST.get("phone_number")
        message = request.POST.get("message")

        if recipient_type == "single" and phone_number:
            # Send to one farmer
            formatted_number = format_phone_number(phone_number)
            try:
                response = sms.send(message, [formatted_number])
                Notification.objects.create(
                    recipient_type="single",
                    phone_number=formatted_number,
                    message=message
                )
                print(f"✅ SMS sent to {formatted_number}: {response}")
                messages.success(request, f"Message sent to {formatted_number}")
            except Exception as e:
                print(f"❌ SMS error: {e}")
                messages.error(request, f"Error sending message: {e}")

        elif recipient_type == "all":
            # Send to all farmers
            farmers = Farmer.objects.all()
            for farmer in farmers:
                phone_attr = getattr(farmer, "phone_number", None) or getattr(farmer, "phone", None)
                if not phone_attr:
                    continue
                formatted_number = format_phone_number(phone_attr)
                try:
                    response = sms.send(message, [formatted_number])
                    Notification.objects.create(
                        recipient_type="all",
                        phone_number=formatted_number,
                        message=message
                    )
                    print(f"✅ SMS sent to {formatted_number}: {response}")
                except Exception as e:
                    print(f"❌ SMS error to {formatted_number}: {e}")
            messages.success(request, "Message sent to all farmers!")

        return redirect("officer_notifications")

    return render(request, "officer/officer_notifications.html", {"notifications": notifications})