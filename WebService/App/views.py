from django.shortcuts import render

from .models import *


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
	photo = gallery.photo_set.all().first()
	comments = photo.photocomment_set.all()
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
