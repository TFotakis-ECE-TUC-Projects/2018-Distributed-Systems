import json
import requests
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from ApplicationService.zoo import zk
from .models import Photo


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


def getStorageService(request, uuid):
	photos = Photo.objects.filter(UUID=uuid).all()
	storageService = {'url': ""}
	if len(photos) != 0:
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
	photoFile = request.FILES['photoFile']
	if len(zk.storageServicesList) == 0:
		return HttpResponseNotFound()
	hadOneSuccessfulTransfer = False
	UUID = ""
	for storageService in zk.storageServicesList:
		print("stogageServiceUrl:" + storageService['url'])
		requestUrl = storageService['url'] + 'uploadPhoto/'
		response = requests.post(requestUrl, files={'photoFile': photoFile})
		if response.ok:
			hadOneSuccessfulTransfer = True
			UUID = json.loads(response.text)['UUID']
			Photo.objects.create(UUID=UUID, StorageService=storageService['name'])
	return JsonResponse({'UUID': UUID}) if hadOneSuccessfulTransfer else HttpResponseNotFound()
