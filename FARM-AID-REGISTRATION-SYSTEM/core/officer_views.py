from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Farmer, AidApplication, Notification
from django.contrib import messages

# Helper decorator — only officers can access these views
def officer_required(view_func):
    return user_passes_test(lambda user: user.is_officer)(view_func)


@login_required
@officer_required
def officer_dashboard(request):
    total_farmers = Farmer.objects.count()
    total_applications = AidApplication.objects.count()
    pending = AidApplication.objects.filter(status='pending').count()
    approved = AidApplication.objects.filter(status='approved').count()
    rejected = AidApplication.objects.filter(status='rejected').count()

    context = {
        'total_farmers': total_farmers,
        'total_applications': total_applications,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
    }
    return render(request, 'officer/officer_dashboard.html', context)


@login_required
@officer_required
def officer_farmers(request):
    farmers = Farmer.objects.all()
    return render(request, 'officer/officer_farmers.html', {'farmers': farmers})


@login_required
@officer_required
def officer_applications(request):
    applications = AidApplication.objects.select_related('farmer').all()
    return render(request, 'officer/officer_applications.html', {'applications': applications})


@login_required
@officer_required
def officer_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'officer/officer_notifications.html', {'notifications': notifications})

@login_required
@officer_required
def update_application_status(request, application_id, status):
    """Allow officer to approve or reject an application"""
    application = get_object_or_404(AidApplication, id=application_id)
    valid_statuses = ['approved', 'rejected']

    if status in valid_statuses:
        application.status = status
        application.save()
        messages.success(request, f"Application for {application.farmer.full_name} has been {status}.")
    else:
        messages.error(request, "Invalid status value.")

    return redirect('officer_applications')
