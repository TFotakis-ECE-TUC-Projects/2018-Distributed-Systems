from django.http import HttpResponse

from .zoo import zk


def status(request):
	response = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
	response += zk.getStatusText()
	response += '</pre>'
	return HttpResponse(response)
