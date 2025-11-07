from mailbox import Message
from django.utils import timezone

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
from .models import AidApplication, Farmer, ContactMessage
from .forms import FarmerForm, AidApplicationForm
from .models import SubAidItem


from .forms import FarmerUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .sms_utils import send_sms_notification
from .models import Notification
from .forms import NotificationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from .forms import AidItemForm
from .models import AidItem




import africastalking

# use africastalking SDK's SMS client (AfricasTalkingGateway import removed)

username = "sandbox"
api_key = "atsk_5b254d369598cb7309f0e80d7faed886f687a79ae551d0cf2d6a0d517fd28a46a4ad4c47"
africastalking.initialize(username, api_key)
sms = africastalking.SMS

import json



applications = []  # temporary store (replace with DB model later)

def apply_aid(request):
    """
    Combined Farmer registration/update + Aid application view with sub-items and quantity tracking.
    """
    farmer = Farmer.objects.filter(user=request.user).first()
    available_items = AidItem.objects.all()  # e.g., Seedlings, Fertilizer, etc.

    if request.method == "POST":
        farmer_form = FarmerForm(request.POST, instance=farmer)
        aid_form = AidApplicationForm(request.POST)

        # ✅ Step 1: Save or update farmer info
        if farmer_form.is_valid():
            farmer = farmer_form.save(commit=False)
            farmer.user = request.user
            farmer.save()
            messages.success(request, "Farmer profile saved successfully ✅")
        else:
            messages.error(request, "Please correct the farmer info errors.")

        # ✅ Step 2: Process aid application
        if farmer and aid_form.is_valid():
            sub_aid_item = aid_form.cleaned_data["sub_aid_item"]
            aid_item = sub_aid_item.aid_item
            quantity_requested = aid_form.cleaned_data["quantity_requested"]

            # ✅ Check if the application window is open
            if not aid_item.is_open_for_application:
                messages.error(
                    request,
                    f"Applications for {aid_item.get_name_display()} are currently closed."
                )
                return redirect("apply_aid")

            # ✅ Check stock availability
            if sub_aid_item.quantity_available < quantity_requested:
                messages.error(
                    request,
                    f"Only {sub_aid_item.quantity_available} {sub_aid_item.name} available. "
                    "Please request a smaller quantity."
                )
                return redirect("apply_aid")

            # ✅ Prevent duplicate applications
            existing_application = AidApplication.objects.filter(
                farmer=farmer,
                sub_aid_item=sub_aid_item
            ).exclude(status="rejected").exists()

            if existing_application:
                messages.error(
                    request,
                    f"You already have an active application for {sub_aid_item.name}."
                )
                return redirect("apply_aid")

            # ✅ Create the aid application
            AidApplication.objects.create(
                farmer=farmer,
                aid_item=aid_item,
                sub_aid_item=sub_aid_item,
                quantity_requested=quantity_requested,
            )

            # ✅ Reduce stock correctly at both sub and main item levels
            sub_aid_item.quantity_available -= quantity_requested
            sub_aid_item.save()

            if hasattr(aid_item, "quantity_available"):
                aid_item.quantity_available = max(aid_item.quantity_available - quantity_requested, 0)
                aid_item.save()

            messages.success(
                request,
                f"Your application for {quantity_requested} {sub_aid_item.name} has been submitted successfully ✅"
            )
            return redirect("dashboard")

    else:
        farmer_form = FarmerForm(instance=farmer)
        aid_form = AidApplicationForm()

    context = {
        "farmer_form": farmer_form,
        "aid_form": aid_form,
        "available_items": available_items,
        "farmer": farmer,
    }

    return render(request, "core/apply_aid.html", context)





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
def cancel_application(request, application_id):
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        messages.error(request, "You are not authorized to cancel this application.")
        return redirect("login")

    application = get_object_or_404(AidApplication, id=application_id, farmer=farmer)

    if application.status == "pending":
        application.status = "cancelled"
        application.save()
        messages.success(request, "Application has been cancelled successfully.")
    else:
        messages.warning(request, "Only pending applications can be cancelled.")

    return redirect("status", id_number=farmer.id_number)






def status_view(request, id_number):
    farmer = get_object_or_404(Farmer, id_number=id_number)
    applications = AidApplication.objects.filter(farmer=farmer)

    return render(request, "core/status.html", {
        "farmer": farmer,
        "applications": applications
    })

@login_required
def reapply_application(request, application_id):
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        messages.error(request, "You are not authorized to reapply.")
        return redirect("login")

    # Fetch the original application
    old_application = get_object_or_404(AidApplication, id=application_id, farmer=farmer)

    # ✅ Check if this farmer has already reapplied based on the same original application
    existing_reapplication = AidApplication.objects.filter(
        farmer=farmer,
        resources_needed=old_application.resources_needed,
        status="pending"
    ).exclude(id=old_application.id).exists()

    if existing_reapplication:
        messages.warning(request, "You have already reapplied for this aid. You can only reapply once.")
        return redirect("status", id_number=farmer.id_number)

    # ✅ Otherwise, allow one reapplication
    new_application = AidApplication.objects.create(
        farmer=farmer,
        resources_needed=old_application.resources_needed,
        status="pending"
    )

    messages.success(request, "Your application has been reapplied successfully.")
    return redirect("status", id_number=farmer.id_number)

def get_sub_items(request, aid_item_id):
    sub_items = SubAidItem.objects.filter(aid_item_id=aid_item_id)
    data = {'sub_items': [{'id': s.id, 'name': s.name} for s in sub_items]}
    return JsonResponse(data)


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




@login_required
def view_messages(request):
    if request.user.is_officer or request.user.is_staff:
        messages_list = ContactMessage.objects.all().order_by("-created_at")
    else:
        # Optional: if farmers should see their own messages
        messages_list = ContactMessage.objects.filter(email=request.user.email)
    return render(request, "officer/view_messages.html", {"messages_list": messages_list})




@login_required
def reply_message(request, message_id):
    msg = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == "POST":
        reply_text = request.POST.get("reply")
        msg.reply = reply_text
        msg.replied_by = request.user
        msg.replied_at = timezone.now()
        msg.is_reply_seen = False  # 👈 farmer hasn’t seen the new reply yet
        msg.save()
        messages.success(request, "Reply sent successfully.")
        return redirect("view_messages")

    return render(request, "officer/reply_message.html", {"msg": msg})

@login_required
def farmer_messages(request):
    messages_list = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at')

    # Mark unseen replies as seen
    unseen_replies = messages_list.filter(reply__isnull=False, is_reply_seen=False)
    unseen_replies.update(is_reply_seen=True)

    return render(request, "core/farmer_messages.html", {"messages_list": messages_list})




@login_required
def available_aid(request):
    """View for farmers to see available aids."""
    aids = AidItem.objects.all().order_by('name')
    return render(request, "core/farmer_aid_list.html", {"aids": aids})


def is_officer(user):
    return user.is_authenticated and user.role in ['officer', 'admin']  # adjust as per your model


@login_required
@user_passes_test(is_officer)
def manage_aid_inventory(request):
    """View for officers/admin to manage aid stock."""
    aids = AidItem.objects.all().order_by('-updated_at')
    return render(request, "core/manage_aid_inventory.html", {"aids": aids})


# Restrict access to only officers and admins
def is_officer_or_admin(user):
    return user.is_authenticated and (user.is_officer or user.is_staff)


@login_required
@user_passes_test(is_officer_or_admin)
def aid_inventory_dashboard(request):
    """
    View for officers and admins to monitor aid stock levels and application periods.
    """
    aid_items = AidItem.objects.all().order_by('name')
    return render(request, "core/aid_inventory_dashboard.html", {"aid_items": aid_items})



@login_required
@user_passes_test(is_officer_or_admin)
def edit_aid_item(request, item_id):
    """
    Allow officers/admins to edit quantity and dates of aid items.
    """
    aid_item = get_object_or_404(AidItem, id=item_id)

    if request.method == "POST":
        form = AidItemForm(request.POST, instance=aid_item)
        if form.is_valid():
            form.save()
            messages.success(request, f"{aid_item.get_name_display()} updated successfully ✅")
            return redirect("aid_inventory_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AidItemForm(instance=aid_item)

    return render(request, "core/edit_aid_item.html", {"form": form, "aid_item": aid_item})