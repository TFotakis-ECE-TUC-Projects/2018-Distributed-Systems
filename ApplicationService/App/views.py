from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ApplicationService.zoo import zk
from .models import *


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


def getStorageService(request, uuid):
	photos = Photo.objects.filter(UUID=uuid).all()
	storageService = {'url': ""}
	for storageService in zk.storageServicesList:
		selectedStorageService = photos.filter(StorageService=storageService['name'])
		if selectedStorageService is not None:
			break
	context = {
		'storageService': storageService['url']
	}
	return JsonResponse(context)


@csrf_exempt
def uploadPhoto(request):
	# photoFile = request.FILES['']
	return HttpResponse(status=200)
