from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from core.models import Farmer, AidApplication


@csrf_exempt
def ussd_callback(request):
    if request.method == "POST":
        session_id = request.POST.get("sessionId", "")
        service_code = request.POST.get("serviceCode", "")
        phone_number = request.POST.get("phoneNumber", "")
        text = request.POST.get("text", "").strip()

        user_response = text.split("*")
        level = len(user_response)

        # --- MAIN MENU ---
        if text == "":
            response = "CON Welcome to FarmAid Kenya\n"
            response += "1. Register as a Farmer\n"
            response += "2. Apply for Aid\n"
            response += "3. Track Application\n"
            response += "4. Exit"

        # --- REGISTER FARMER ---
        elif user_response[0] == "1":
            if level == 1:
                response = "CON Enter your Full Name:"
            elif level == 2:
                response = "CON Enter your ID Number:"
            elif level == 3:
                response = "CON Enter your County:"
            elif level == 4:
                response = "CON Enter your Sub-County:"
            elif level == 5:
                response = "CON Enter your Ward:"
            elif level == 6:
                response = "CON Enter your Farm Size (in acres):"
            elif level == 7:
                response = (
                    "CON Select your Farming Type:\n"
                    "1. Crop Farming\n"
                    "2. Livestock Farming\n"
                    "3. Mixed Farming"
                )
            elif level == 8:
                try:
                    full_name = user_response[1]
                    id_number = user_response[2]
                    county = user_response[3]
                    sub_county = user_response[4]
                    ward = user_response[5]
                    farm_size = user_response[6]
                    farming_choice = user_response[7]

                    farming_type_map = {
                        "1": "crop",
                        "2": "livestock",
                        "3": "mixed",
                    }

                    farming_type = farming_type_map.get(farming_choice, "crop")

                    Farmer.objects.get_or_create(
                        phone_number=phone_number,
                        defaults={
                            "full_name": full_name,
                            "id_number": id_number,
                            "county": county,
                            "sub_county": sub_county,
                            "ward": ward,
                            "farm_size": farm_size,
                            "farming_type": farming_type,
                        },
                    )

                    response = "END Registration successful! Welcome to FarmAid Kenya."

                except Exception as e:
                    print("Error saving farmer:", e)
                    response = "END Something went wrong. Please try again."
            else:
                response = "END Invalid input. Please start again."

        # --- APPLY FOR AID ---
        elif user_response[0] == "2":
            try:
                farmer = Farmer.objects.get(phone_number=phone_number)
            except Farmer.DoesNotExist:
                response = "END You need to register first to apply for aid."
                return HttpResponse(response)

            if level == 1:
                response = (
                    "CON Select Aid Type:\n"
                    "1. Seedlings\n"
                    "2. Fertilizers\n"
                    "3. Pesticides\n"
                    "4. Livestock Vaccines\n"
                    "5. Equipment\n"
                    "6. Financial Support"
                )

            elif level == 2:
                aid_type_map = {
                    "1": "seedlings",
                    "2": "fertilizers",
                    "3": "pesticides",
                    "4": "livestock_vaccines",
                    "5": "equipment",
                    "6": "financial_support",
                }

                aid_type = aid_type_map.get(user_response[1])
                if not aid_type:
                    response = "END Invalid selection. Please try again."
                else:
                    # --- Prevent duplicate pending aid applications ---
                    existing = AidApplication.objects.filter(
                        farmer=farmer,
                        resources_needed=aid_type,
                        status="pending"
                    ).exists()

                    if existing:
                        response = (
                            f"END You already have a pending {aid_type.replace('_', ' ')} aid application.\n"
                            f"Please wait for it to be processed before applying again."
                        )
                    else:
                        AidApplication.objects.create(
                            farmer=farmer,
                            resources_needed=aid_type,
                            status="pending",
                        )

                        response = (
                            f"END Your {aid_type.replace('_', ' ')} aid application "
                            f"has been received successfully.\n"
                            f"Location: {farmer.county}, {farmer.sub_county}, {farmer.ward}."
                        )
            else:
                response = "END Invalid option. Please try again."

        elif user_response[0] == "3":
            try:
                farmer = Farmer.objects.get(phone_number=phone_number)
                applications = AidApplication.objects.filter(farmer=farmer).order_by('-applied_at')

                if applications.exists():
                    response = "END Your aid application statuses:\n"
                    for app in applications[:5]:
        
                        response += f"- {app.resources_needed.replace('_', ' ').title()}: {app.status.title()} ({app.applied_at.date()})\n"

                    response += "\nThank you for using FarmAid Kenya."
                else:
                    response = "END You have no aid applications yet."
            except Farmer.DoesNotExist:
                response = "END You need to register first to track applications."

        elif user_response[0] == "4":
            response = "END Thank you for using FarmAid Kenya."

        else:
            response = "END Invalid option. Please try again."

    # ✅ Always return a response, no matter what
    return HttpResponse(response)


