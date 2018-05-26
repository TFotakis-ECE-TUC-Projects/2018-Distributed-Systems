from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect


def loginView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="login.html", context=context)
	else:
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			login(request, user)
			return redirect(request.GET.get('callback'), permanent=True)
		else:
			return redirect('loginView')


def registerView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="register.html", context=context)
	else:
		User.objects.create_user(
			username=request.POST['username'],
			email=request.POST['email'],
			password=request.POST['password'],
			first_name=request.POST['name'],
			last_name=request.POST['surname']
		)
		return HttpResponse(status=200)
