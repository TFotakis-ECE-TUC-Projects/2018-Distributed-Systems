import json
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
		print("Creating " + settings.ZOOKEEPER_NODE_ID + " node")
		acl = make_digest_acl(settings.ZOOKEEPER_USER, settings.ZOOKEEPER_PASSWORD, all=True)
		dataJsonDict = {
			'SERVER_HOSTNAME': settings.ZOOKEEPER_HOST,
			'SERVER_PORT': settings.SERVER_PORT,
			'SERVER_SCHEME': settings.SERVER_SCHEME,
			'CONTEXT': settings.CONTEXT
		}
		self.__zkcon.create_async(
			path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_NODE_ID,
			value=json.JSONEncoder().encode(dataJsonDict).encode(),
			ephemeral=settings.ZOOKEEPER_NODE_EPHIMERAL
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

	def getAvailableFs(self):
		return self.__fsList

	def getZooConnection(self):
		return self.__zkcon


# imported only once per module
zk = Zooconf()
