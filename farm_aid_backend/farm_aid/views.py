# farmapp/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import FarmerApplication
from django.shortcuts import render

def register_view(request):
    return render(request, "farm_aid/register.html")

@require_http_methods(["POST"])
def submit_application(request):
    try:
        full_name = request.POST.get("full_name")
        id_number = request.POST.get("id_number")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")

        county = request.POST.get("county")
        sub_county = request.POST.get("sub_county")
        ward = request.POST.get("ward")
        farm_size = request.POST.get("farm_size")
        farming_type = request.POST.get("farming_type")
        resources_needed = request.POST.get("resources_needed")

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Save to DB
        app = FarmerApplication.objects.create(
            full_name=full_name,
            id_number=id_number,
            phone_number=phone_number,
            email=email,
            county=county,
            sub_county=sub_county,
            ward=ward,
            farm_size=farm_size,
            farming_type=farming_type,
            resources_needed=resources_needed,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
        )

        return JsonResponse({"id": app.id, "message": "Application submitted successfully"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
