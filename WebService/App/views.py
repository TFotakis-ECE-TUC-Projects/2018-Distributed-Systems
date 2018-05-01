from django.conf import settings
from django.http import HttpResponse

from .zoo import zk


def status(request):
	response = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
	response += getStatusText()
	response += '</pre>'
	return HttpResponse(response)


def getStatusText():
	result = ""
	zkCon = zk.getZooConnection()
	try:
		rootChildren = zkCon.get_children(settings.ZOOKEEPER_ROOT)
		for child in rootChildren:
			data, stat = zkCon.get(settings.ZOOKEEPER_ROOT + child)
			result += child + " data: " + data.decode("utf-8") + "\n"
			try:
				grandchildren = zkCon.get_children(settings.ZOOKEEPER_ROOT + child)
				for grandchild in grandchildren:
					data, stat = zkCon.get(settings.ZOOKEEPER_ROOT + grandchild)
					result += grandchild + " data: " + data.decode("utf-8") + "\n"
			except Exception:
				pass
		return result
	except Exception:
		pass
	return result
