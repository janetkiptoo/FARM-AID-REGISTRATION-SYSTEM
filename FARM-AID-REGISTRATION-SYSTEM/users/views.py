from django.http import HttpResponse

def profile(request):
    return HttpResponse("Hello from the Users app!")
