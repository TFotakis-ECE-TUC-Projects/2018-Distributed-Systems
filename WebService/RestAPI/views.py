from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect

from App.models import *
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
	Photo.objects.create(Gallery_id=galleryId, UUID=photoFile.name, Description=description, Location=location)

	applicationServiceData = zk.getNodeData('ApplicationService')
	applicationServiceUrl = applicationServiceData['SERVER_HOSTNAME'] + ':' + applicationServiceData['SERVER_PORT']
	requestUrl = applicationServiceUrl + '/uploadPhoto/'
	response = requests.post(requestUrl, data={'csrfmiddlewaretoken': request.POST['csrfmiddlewaretoken']}, files={'photoFile': photoFile})

	return redirect('App:gallery', id=galleryId)
