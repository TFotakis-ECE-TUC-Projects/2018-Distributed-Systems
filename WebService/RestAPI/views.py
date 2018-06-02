import json
import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

from App.models import Friendship, Photo, PhotoComment
from WebService import settings
from WebService.cryptography import cr
from WebService.zoo import zk

LOGIN_URL = 'login?system=' + settings.ZOOKEEPER_NODE_ID + '&callback=' + settings.SERVER_HOSTNAME + ':' + settings.SERVER_PORT + '/'


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def addComment(request, photoId):
	PhotoComment.objects.create(User_id=request.user.id, Photo_id=photoId, Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deleteComment(request, commentId):
	PhotoComment.objects.get(id=commentId).delete()
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def updateComment(request, commentId):
	PhotoComment.objects.filter(id=commentId).update(Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
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


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def makeFriendship(request, userId, friendId):
	Friendship.objects.create(User_id=userId, Friend_id=friendId)
	return redirect('App:listOfUsers')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deleteFriendship(request, userId, friendId):
	Friendship.objects.filter(User_id=userId, Friend_id=friendId).delete()
	return redirect('App:listOfUsers')


def loginExternal(request):
	userData = json.loads(request.GET.get('token'))
	sharedKey = ''
	for authService in zk.authenticationServiceList:
		if authService['name'] == userData['issuer']:
			sharedKey = authService['sharedKey']
			break
	decrypted = cr.defaultDecrypt(inputData=userData['crypted'], sharedKeyBase64=sharedKey)
	return redirect('App:home')
