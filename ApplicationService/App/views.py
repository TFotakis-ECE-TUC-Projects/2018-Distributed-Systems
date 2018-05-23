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
	storageServices = zk.getNodeData('StorageServices')['CHILDREN']
	storageService = ''
	for storageService in storageServices:
		selectedStorageService = photos.filter(StorageService=storageService)
		if selectedStorageService is not None:
			break
	storageServiceData = zk.getNodeData(storageService)
	context = {
		'storageService': storageServiceData['SERVER_HOSTNAME'] + ':' + storageServiceData['SERVER_PORT']
	}
	return JsonResponse(context)


@csrf_exempt
def uploadPhoto(request):
	# photoFile = request.FILES['']
	return HttpResponse(status=200)
