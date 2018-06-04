import json
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from WebService import settings
from WebService.cryptography import cr
from WebService.zoo import zk
from .models import Profile, Friendship, Gallery, Photo

LOGIN_URL = 'login/'


def loginView(request):
	if request.method == 'GET':
		authServices = zk.authenticationServiceList
		context = {
			'authServices': authServices,
			'serverUrl': settings.SERVER_HOSTNAME + ((':' + settings.SERVER_PORT) if settings.SERVER_PORT != '' else '')
		}
		return render(request=request, template_name="App/login.html", context=context)
	else:
		authService = {
			'url': ''
		}
		for authService in zk.authenticationServiceList:
			if authService['name'] == settings.DEFAULT_AUTH_SERVICE_NAME:
				break
		url = authService['loginUrl'] + '/'
		newRequest = requests.get(url)
		csrftoken = newRequest.cookies['csrftoken']
		header = {'X-CSRFToken': csrftoken}
		cookies = {'csrftoken': csrftoken}
		context = {
			'username': request.POST['username'],
			'password': request.POST['password'],
			'redirectmethod': 'POST'
		}
		response = requests.post(url=url, data=context, headers=header, cookies=cookies)
		userData = json.loads(json.loads(response.content)['token'])
		sharedKey = ''
		for authService in zk.authenticationServiceList:
			if authService['name'] == userData['issuer']:
				sharedKey = authService['sharedKey']
				break
		decrypted = cr.defaultDecrypt(inputData=userData['crypted'].replace(' ', '+'), sharedKeyBase64=sharedKey)
		userid = json.loads(decrypted['data'])['userid']
		user = Profile.objects.get(AuthService=userData['issuer'], AuthServiceUserId=userid).User
		login(request, user)
		return redirect('App:home')


def registerView(request):
	if request.method == 'GET':
		authServices = zk.authenticationServiceList
		context = {
			'authServices': authServices,
			'serverUrl': settings.SERVER_HOSTNAME + ((':' + settings.SERVER_PORT) if settings.SERVER_PORT != '' else '')
		}
		return render(request=request, template_name="App/register.html", context=context)
	else:
		authService = {
			'url': ''
		}
		for authService in zk.authenticationServiceList:
			if authService['name'] == settings.DEFAULT_AUTH_SERVICE_NAME:
				break
		url = authService['registerUrl'] + '/'
		newRequest = requests.get(url)
		csrftoken = newRequest.cookies['csrftoken']
		header = {'X-CSRFToken': csrftoken}
		cookies = {'csrftoken': csrftoken}
		context = {
			'username': request.POST['username'],
			'firstname': request.POST['firstname'],
			'lastname': request.POST['lastname'],
			'email': request.POST['email'],
			'password': request.POST['password'],
			'redirectmethod': 'POST'
		}
		response = requests.post(url=url, data=context, headers=header, cookies=cookies)
		if response.ok:
			userData = json.loads(json.loads(response.content)['token'])
			sharedKey = ''
			for authService in zk.authenticationServiceList:
				if authService['name'] == userData['issuer']:
					sharedKey = authService['sharedKey']
					break
			decrypted = cr.defaultDecrypt(inputData=userData['crypted'], sharedKeyBase64=sharedKey)
			data = json.loads(decrypted['data'])
			usermeta = json.loads(data['usermeta'])
			user = User.objects.create_user(
				username=usermeta['nick'] + "-" + userData['issuer'],
				first_name=usermeta['name'].split()[0],
				last_name=usermeta['name'].split()[1],
				email=usermeta['email'],
			)
			if user is not None:
				user.profile.AuthService = userData['issuer']
				user.profile.AuthServiceUserId = data['userid']
				user.save()
				login(request, user)
				return redirect('App:home')
			else:
				return redirect('App:register')
		return redirect('App:register')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def logoutView(request):
	logout(request)
	return redirect('App:home')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def homeView(request):
	# People that have me as a friend can show me their photos
	friends = Friendship.objects.filter(Friend_id=request.user.id).all().values_list('User', flat=True)
	photos = Photo.objects.filter(Gallery__Owner__in=friends).all().order_by('-UploadDateTime')
	context = {
		'photos': photos
	}
	return render(request=request, template_name="App/home.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def profileView(request, id):
	user = User.objects.get(id=id)
	context = {
		'user': user,
		'isFriend': id == request.user.id
	}
	return render(request=request, template_name="App/profile.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def myProfileView(request):
	return profileView(request, request.user.id)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def galleryView(request, id):
	gallery = Gallery.objects.get(id=id)
	context = {'gallery': gallery}
	return render(request=request, template_name="App/gallery.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def uploadPhotoView(request):
	context = {
		'galleries': Gallery.objects.filter(Owner=request.user.id).all()
	}
	return render(request=request, template_name="App/uploadPhoto.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def uploadProfilePhotoView(request):
	context = {}
	return render(request=request, template_name="App/uploadProfilePhoto.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def listOfUsers(request):
	userId = request.user.id
	knownUsers = Friendship.objects.filter(User_id=userId)
	excludeList = knownUsers.values_list('Friend_id', flat=True)
	unknownUsers = Profile.objects.exclude(id=userId).exclude(id__in=excludeList)
	context = {'unknownUsers': unknownUsers, 'knownUsers': knownUsers}
	return render(request, template_name="App/userList.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def createGallery(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="App/createGallery.html", context=context)
	else:
		userId = request.user.id
		Gallery.objects.create(Owner_id=userId, Name=request.POST['name'])
		return redirect('App:myProfile')
