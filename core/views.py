from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, this is the core index page!")

def submit_application(request):
    return HttpResponse("Application submitted!")
