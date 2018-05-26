import json
import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

from App.models import Friendship, Photo, PhotoComment
from WebService.zoo import zk


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


def addComment(request, photoId):
	PhotoComment.objects.create(User_id=1, Photo_id=photoId, Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


def deleteComment(request, commentId):
	PhotoComment.objects.get(id=commentId).delete()
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


def updateComment(request, commentId):
	PhotoComment.objects.filter(id=commentId).update(Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


def uploadPhoto(request):
	galleryId = request.POST['galleryId']
	description = request.POST['Description']
	location = request.POST['Location']
	photoFile = request.FILES['photoFile']

	requestUrl = zk.applicationService + 'uploadPhoto/'
	response = requests.post(requestUrl, files={'photoFile': photoFile})

	if response.ok:
		UUID = json.loads(response.content)['UUID']
		Photo.objects.create(Gallery_id=galleryId, UUID=UUID, Description=description, Location=location)
		return redirect('App:gallery', id=galleryId)
	# Todo: Replace harcoded user
	return redirect('App:uploadPhoto', 1)


def makeFriendship(request, userId, friendId):
	Friendship.objects.create(User_id=userId, Friend_id=friendId)
	return redirect('App:listOfUsers')


def deleteFriendship(request, userId, friendId):
	Friendship.objects.filter(User_id=userId, Friend_id=friendId).delete()
	return redirect('App:listOfUsers')
