from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
	print("Logged in")


# return redirect(request.GET.get('callback'))
# return redirect('https://www.google.com')


@csrf_exempt
def register(request):
	pass
