from django.http import HttpResponse
from core.models import Farmer, AidApplication

def ussd_callback(request):
    session_id = request.POST.get("sessionId", None)
    service_code = request.POST.get("serviceCode", None)
    phone_number = request.POST.get("phoneNumber", None)
    text = request.POST.get("text", "")

    # Split the text input
    user_response = text.split("*")

    if text == "":
        # Main Menu
        response = "CON Welcome to FarmAid Kenya\n"
        response += "1. Register as a Farmer\n"
        response += "2. Apply for Aid\n"
        response += "3. Check Aid Status"
    elif text == "1":
        response = "CON Enter your full name"
    elif len(user_response) == 2 and user_response[0] == "1":
        name = user_response[1]
        # Register Farmer if not exists
        farmer, created = Farmer.objects.get_or_create(phone_number=phone_number, defaults={'name': name})
        response = "END Registration successful. Thank you, " + name
    elif text == "2":
        response = "CON Enter type of aid you need (e.g., Fertilizer)"
    elif len(user_response) == 2 and user_response[0] == "2":
        aid_type = user_response[1]
        farmer = Farmer.objects.filter(phone_number=phone_number).first()
        if farmer:
            AidApplication.objects.create(farmer=farmer, aid_type=aid_type, status="Pending")
            response = "END Aid application for " + aid_type + " submitted successfully."
        else:
            response = "END You must register first (Dial again and choose option 1)"
    elif text == "3":
        farmer = Farmer.objects.filter(phone_number=phone_number).first()
        if farmer:
            apps = AidApplication.objects.filter(farmer=farmer)
            if apps.exists():
                app = apps.last()
                response = f"END Your latest aid ({app.aid_type}) status: {app.status}"
            else:
                response = "END No aid applications found."
        else:
            response = "END You are not registered. Please register first."
    else:
        response = "END Invalid choice. Try again."

    return HttpResponse(response, content_type="text/plain")
