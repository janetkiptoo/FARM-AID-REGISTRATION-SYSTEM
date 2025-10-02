from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

applications = []  # temporary store (replace with DB model later)

@csrf_exempt
def submit_application(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        applications.append({
            "name": data.get("name"),
            "id_number": data.get("id_number"),
            "farm_size": data.get("farm_size"),
            "status": "Pending",
        })
        return JsonResponse({"message": "Application received"}, status=201)

    elif request.method == "GET":
        id_number = request.GET.get("id_number")
        for app in applications:
            if app["id_number"] == id_number:
                return JsonResponse(app, status=200)
        return JsonResponse({"error": "Application not found"}, status=404)

def index(request):
    
    return render(request, "core/index.html")

def login_view(request):
     if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
     return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def register(request):
     if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")
     
     return render(request, "core/register.html")

@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")

def status(request):
    return render(request, "core/status.html")
