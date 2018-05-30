import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from AuthService.zoo import zk


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
		context = {
			'username': request.POST['username'],
			'email': request.POST['email'],
			'password': request.POST['password'],
			'firstname': request.POST['firstname'],
			'lastname': request.POST['lastname']
		}
		url = zk.webService + 'register/'
		csrftoken = requests.get(url).cookies['csrftoken']
		header = {'X-CSRFToken': csrftoken}
		cookies = {'csrftoken': csrftoken}
		response = requests.post(url=url, data=context, headers=header, cookies=cookies)
		if response.ok:
			user = User.objects.create_user(
				username=request.POST['username'],
				email=request.POST['email'],
				password=request.POST['password'],
				first_name=request.POST['firstname'],
				last_name=request.POST['lastname']
			)
			login(request, user)
			nextResponse = redirect(request.GET.get('callback'), permanent=True)
			nextResponse.set_cookie('csrftoken', response.cookies['csrftoken'])
			return nextResponse
		return redirect('App:register', permanent=True)


def authService(request):
	response = redirect('App:webService', permanent=True)
	response.set_cookie('csrftoken', 123)
	return response


def webService(request):
	return HttpResponse(status=200)
