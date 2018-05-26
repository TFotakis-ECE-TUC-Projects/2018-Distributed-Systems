from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
	print("Logged in")
	pass


def register(request):
	pass
