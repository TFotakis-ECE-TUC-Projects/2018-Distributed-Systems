import json
import threading
from django.conf import settings
from kazoo.client import KazooClient
from kazoo.security import make_digest_acl


class Zooconf:
	__zkcon = None
	__fsList = None

	def __init__(self):
		self.__zooConnect()
		self.__publishService()
		self.__initFsWatches()

	def __zooConnect(self):
		print("Connecting to ZooKeeper")
		self.__zkcon = KazooClient(hosts=settings.ZOOKEEPER_HOST)
		self.__zkcon.start()
		digest_auth = "%s:%s" % (settings.ZOOKEEPER_USER, settings.ZOOKEEPER_PASSWORD)
		self.__zkcon.add_auth("digest", digest_auth)

	def __publishService(self):
		acl = make_digest_acl(settings.ZOOKEEPER_USER, settings.ZOOKEEPER_PASSWORD, all=True)
		dataJsonDict = {
			'SERVER_HOSTNAME': settings.ZOOKEEPER_HOST,
			'SERVER_PORT': settings.SERVER_PORT,
			'CHILDREN': []
		}
		if self.__zkcon.exists(path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID):
			self.__zkcon.set(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID,
				value=json.JSONEncoder().encode(dataJsonDict).encode()
			)
		else:
			self.__zkcon.create_async(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID,
				value=json.JSONEncoder().encode(dataJsonDict).encode(),
				ephemeral=settings.ZOOKEEPER_NODE_EPHIMERAL
			)
		if settings.ZOOKEEPER_PATH_TO_NODE != '':
			data, stat = self.__zkcon.get(settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE)
			dataJsonDict = json.loads(data.decode("utf-8"))
			if settings.ZOOKEEPER_NODE_ID not in dataJsonDict['CHILDREN']:
				dataJsonDict['CHILDREN'].append(settings.ZOOKEEPER_NODE_ID)
			self.__zkcon.set(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE,
				value=json.JSONEncoder().encode(dataJsonDict).encode()
			)

	def __initFsWatches(self):
		# lists are supposed to be thread safe in python
		self.__fsList = []

		# Called immediately, and from then on
		@self.__zkcon.ChildrenWatch(settings.ZOOKEEPER_ROOT + "fileservices")
		def watch_children(children):
			self.__fsList = []
			print("Children are now: %s" % children)
			for child in children:
				self.__fsList.append(child)

	def getAvailableFs(self): return self.__fsList

	def getZooConnection(self): return self.__zkcon

	def getStatusText(self):
		result = "{\n"
		try:
			rootChildren = self.__zkcon.get_children(settings.ZOOKEEPER_ROOT)
			for child in rootChildren:
				data, stat = self.__zkcon.get(settings.ZOOKEEPER_ROOT + child)
				result += '\t"' + child + '": ' + data.decode("utf-8") + "\n"
				try:
					grandchildren = self.__zkcon.get_children(settings.ZOOKEEPER_ROOT + child)
					for grandchild in grandchildren:
						data, stat = self.__zkcon.get(settings.ZOOKEEPER_ROOT + child + '/' + grandchild)
						result += '\t"' + grandchild + '": ' + data.decode("utf-8") + "\n"
					data, stat = self.__zkcon.get(settings.ZOOKEEPER_ROOT + child + '/')
					dataJsonDict = json.loads(data.decode("utf-8"))
					dataJsonDict['CHILDREN'] = grandchildren
					self.__zkcon.set(
						path=settings.ZOOKEEPER_ROOT + child,
						value=json.JSONEncoder().encode(dataJsonDict).encode()
					)
				except Exception:
					pass
			return result + '}'
		except Exception:
			self.__zooConnect()
			return self.getStatusText()


def printit():
	threading.Timer(300.0, printit).start()
	print("Heartbeat")
	print(zk.getStatusText())


zk = Zooconf()
printit()
