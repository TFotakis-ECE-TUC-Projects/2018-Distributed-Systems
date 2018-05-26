from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from StorageService.settings import MEDIA_ROOT
from StorageService.zoo import zk


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


def getImage(request, filename):
	try:
		with open(MEDIA_ROOT + filename, "rb") as f:
			return HttpResponse(f.read(), content_type="image/jpeg")
	except IOError:
		return HttpResponseNotFound()


@csrf_exempt
def uploadPhoto(request):
	path = default_storage.save(request.FILES['photoFile'].name, request.FILES['photoFile'])
	return JsonResponse({'UUID': path})
