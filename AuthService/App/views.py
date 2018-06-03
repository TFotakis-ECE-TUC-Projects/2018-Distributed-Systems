import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from urllib.parse import urlencode

from AuthService import settings
from AuthService.cryptography import cr


def createLoginResponse(
		dataErrorMessage='',
		authIdentifier='',
		systemIdentifier='',
		userid='',
		validtill='',
		name='',
		nick='',
		email=''
):
	if dataErrorMessage != '':
		data = {
			"error": dataErrorMessage,
			"data": ''
		}
		return data
	usermeta = {
		"name": name,
		"nick": nick,
		"email": email
	}
	nonCryptedMessage = {
		"AUTHID": authIdentifier,
		"SID": systemIdentifier,
		"userid": userid,
		"validtill": validtill,
		"usermeta": json.dumps(usermeta)
	}
	encryptedMessage = cr.defaultEncrypt(json.dumps(nonCryptedMessage))
	token = {
		"error": encryptedMessage['error'],
		"issuer": authIdentifier,
		"crypted": encryptedMessage['data']
	}
	data = {
		"error": dataErrorMessage,
		"token": json.dumps(token)
	}
	return data


def loginView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="login.html", context=context)
	else:
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			login(request, user)
			loginResponse = createLoginResponse(
				dataErrorMessage='',
				authIdentifier=settings.ZOOKEEPER_NODE_ID,
				systemIdentifier=settings.AUTH_SYSTEM,
				userid=user.id,
				validtill='',
				name=user.first_name + ' ' + user.last_name,
				nick=user.username,
				email=user.email
			)
			dataQuery = '?' + urlencode(loginResponse)
			if request.GET.get('callback') != '/':
				return redirect(request.GET.get('callback') + dataQuery, permanent=True)
			else:
				return JsonResponse(loginResponse)
		else:
			return redirect('loginView')


def registerView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="register.html", context=context)
	else:
		user = User.objects.create_user(
			username=request.POST['username'],
			email=request.POST['email'],
			password=request.POST['password'],
			first_name=request.POST['firstname'],
			last_name=request.POST['lastname']
		)
		if user is not None:
			login(request, user)
			loginResponse = createLoginResponse(
				dataErrorMessage='',
				authIdentifier=settings.ZOOKEEPER_NODE_ID,
				systemIdentifier=settings.AUTH_SYSTEM,
				userid=user.id,
				validtill='',
				name=user.first_name + ' ' + user.last_name,
				nick=user.username,
				email=user.email
			)
			dataQuery = '?' + urlencode(loginResponse)
			if request.GET.get('callback') != '/':
				return redirect(request.GET.get('callback') + dataQuery, permanent=True)
			else:
				return JsonResponse(loginResponse)
		else:
			return redirect('registerView')


def authService(request):
	response = redirect('App:webService', permanent=True)
	response.set_cookie('csrftoken', 123)
	return response


def webService(request):
	return HttpResponse(status=200)
