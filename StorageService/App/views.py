from django.http import *

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
