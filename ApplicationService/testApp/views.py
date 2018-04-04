from django.http import HttpResponse


# Create your views here.
def home(request):
	return HttpResponse("<h1>Ola kompliet</h1>")


message = ""


def messageView(request):
	return HttpResponse("<h1>" + message + "</h1>")


def setMessage(request, givenMessage):
	global message
	message = givenMessage
	return HttpResponse(status=200)
