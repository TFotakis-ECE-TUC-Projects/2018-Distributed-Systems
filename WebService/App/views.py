import requests
from django.shortcuts import render, redirect

from .models import User, Friendship, Gallery


def homeView(request):
	context = {
		'users': User.objects.all()
	}
	return render(request=request, template_name="App/home.html", context=context)


def profileView(request, id):
	user = User.objects.get(id=id)
	context = {'user': user}
	return render(request=request, template_name="App/profile.html", context=context)


def galleryView(request, id):
	gallery = Gallery.objects.get(id=id)
	context = {'gallery': gallery}
	return render(request=request, template_name="App/gallery.html", context=context)


def uploadPhotoView(request, ownerId):
	context = {
		'galleries': Gallery.objects.filter(Owner=ownerId).all()
	}
	return render(request=request, template_name="App/uploadPhoto.html", context=context)


def listOfUsers(request):
	# Todo: change user id from being hardcoded
	userId = 1
	knownUsers = Friendship.objects.filter(User_id=userId)
	excludeList = knownUsers.values_list('Friend_id', flat=True)
	unknownUsers = User.objects.exclude(id=userId).exclude(id__in=excludeList)
	context = {'unknownUsers': unknownUsers, 'knownUsers': knownUsers}

	return render(request, template_name="App/userList.html", context=context)


def loginView(request):
	if request.method == 'GET':
		context = {}
		return render(request=request, template_name="App/login.html", context=context)
	else:
		requests.post('http://127.0.0.1:8003/api/login', data={})
		return redirect('App:home')


# user = authenticate(username=request.POST['username'], password=request.POST['password'])
# if user is not None:
# 	login(request, user)
# 	return redirect(request.GET.get('callback'), permanent=True)
# else:
# 	return redirect('loginView')


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
