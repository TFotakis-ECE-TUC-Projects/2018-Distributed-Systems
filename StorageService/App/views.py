from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from StorageService import settings
from StorageService.settings import MEDIA_ROOT
from StorageService.zoo import zk
from StorageService.cryptography import cr


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


def getImage(request):
	filename = request.GET['uuid']
	username = request.GET['username']
	hmac = request.GET['hmac'].replace(' ', '+')
	filenamePlusUsername = cr.defaultDecrypt(inputData=hmac, sharedKeyBase64=settings.SHARED_KEY_BASE_64)
	if filenamePlusUsername['data'] == filename + username:
		try:
			with open(MEDIA_ROOT + filename, "rb") as f:
				return HttpResponse(f.read(), content_type="image/jpeg")
		except IOError:
			return HttpResponseNotFound()
	else:
		return HttpResponseNotAllowed()


@csrf_exempt
def uploadPhoto(request):
	path = default_storage.save(request.FILES['photoFile'].name, request.FILES['photoFile'])
	return JsonResponse({'UUID': path})
