from django.http import HttpResponse
import requests
from django.conf import settings


# Create your views here.
def home(request):
	return HttpResponse("<h1>Ola kompliet</h1>")


def messageView(request, message):
	response = requests.get(settings.APPLICATION_SERVICE_URL + "setMessage/" + message)
	return HttpResponse(response)
