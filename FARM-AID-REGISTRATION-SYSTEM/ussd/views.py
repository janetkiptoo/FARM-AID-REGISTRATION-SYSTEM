from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from core.models import Farmer, AidApplication  # ✅ make sure AidApplication is imported


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

        # --- REGISTER AS FARMER ---
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
                response = "CON Select your Farming Type:\n1. Crop Farming\n2. Livestock Farming\n3. Mixed Farming"
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
                response = "END Invalid input. Please try again."

        # --- APPLY FOR AID ---
        elif user_response[0] == "2":
            try:
                farmer = Farmer.objects.get(phone_number=phone_number)
            except Farmer.DoesNotExist:
                response = "END You need to register first to apply for aid."
                return HttpResponse(response)

            if level == 1:
                response = "CON Select Aid Type:\n1. Fertilizer\n2. Seeds\n3. Livestock Support"
            elif level == 2:
                response = "CON Enter a short reason for your request:"
            elif level == 3:
                aid_type_map = {"1": "Fertilizer", "2": "Seeds", "3": "Livestock Support"}
                aid_type = aid_type_map.get(user_response[1], "Other")
                reason = user_response[2]

                AidApplication.objects.create(
                    farmer=farmer,
                    aid_type=aid_type,
                    reason=reason,
                    status="Pending",
                )
                response = f"END Your {aid_type} aid application has been received."
            else:
                response = "END Invalid input. Please try again."

        # --- TRACK APPLICATION (coming soon) ---
        elif user_response[0] == "3":
            response = "END Feature coming soon."

        # --- EXIT ---
        elif user_response[0] == "4":
            response = "END Thank you for using FarmAid Kenya."

        # --- INVALID OPTION ---
        else:
            response = "END Invalid option. Please try again."

        return HttpResponse(response)
