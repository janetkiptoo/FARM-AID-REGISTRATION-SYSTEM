from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import OfficerRegistrationForm



def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password1"]
        confirm_password = request.POST["password2"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "users/register.html")


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
     return render(request, "users/login.html")




def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


def register_officer(request):
    if request.method == 'POST':
        form = OfficerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('officer_login')
    else:
        form = OfficerRegistrationForm()
    return render(request, 'users/officer_register.html', {'form': form})

def officer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'is_officer') and user.is_officer:
            login(request, user)
            return redirect('officer_dashboard')  # officer dashboard URL name
        else:
            messages.error(request, "Invalid credentials or not authorized as officer.")
    return render(request, 'users/officer_login.html')


def officer_logout(request):
    logout(request)
    return redirect('officer_login')