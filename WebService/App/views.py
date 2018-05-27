import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from WebService import settings
from .models import Profile, Friendship, Gallery, Photo

LOGIN_URL = '/login?system=' + settings.ZOOKEEPER_NODE_ID  # + '&callback=https://www.google.com'


def loginView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="App/login.html", context=context)
	else:
		try:
			requests.post('http://127.0.0.1:8003/api/login', data={})
		except Exception:
			pass
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			login(request, user)
			# return redirect('App:home')
			return redirect(request.GET.get('callback'), permanent=True)
		else:
			return redirect('loginView')


def registerView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="App/register.html", context=context)
	else:
		return redirect('App:home')


# User.objects.create_user(
# 	username=request.POST['username'],
# 	email=request.POST['email'],
# 	password=request.POST['password'],
# 	first_name=request.POST['name'],
# 	last_name=request.POST['surname']
# )
# return HttpResponse(status=200)

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
	user = Profile.objects.get(id=id)
	context = {'user': user}
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
def uploadPhotoView(request, ownerId):
	context = {
		'galleries': Gallery.objects.filter(Owner=ownerId).all()
	}
	return render(request=request, template_name="App/uploadPhoto.html", context=context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def listOfUsers(request):
	# Todo: change user id from being hardcoded
	userId = request.user.id
	knownUsers = Friendship.objects.filter(User_id=userId)
	excludeList = knownUsers.values_list('Friend_id', flat=True)
	unknownUsers = Profile.objects.exclude(id=userId).exclude(id__in=excludeList)
	context = {'unknownUsers': unknownUsers, 'knownUsers': knownUsers}

	return render(request, template_name="App/userList.html", context=context)
