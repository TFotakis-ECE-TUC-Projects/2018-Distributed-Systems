import json
import threading
from django.conf import settings
from kazoo.client import KazooClient
from kazoo.security import make_digest_acl


class Zooconf:
	connection = None
	webService = None
	applicationService = None
	storageServicesList = None
	authenticationServiceList = None
	status = None

	def initialize(self):
		self.__zooConnect()
		self.__publishService()
		self.__initAuthenticationServiceWatches()
		self.__initStorageServiceWatches()
		self.heartbeat()

	def __zooConnect(self):
		print("Connecting to ZooKeeper")
		self.connection = KazooClient(hosts=settings.ZOOKEEPER_HOST)
		self.connection.start()
		digest_auth = "%s:%s" % (settings.ZOOKEEPER_USER, settings.ZOOKEEPER_PASSWORD)
		self.connection.add_auth("digest", digest_auth)

	def __publishService(self):
		acl = make_digest_acl(settings.ZOOKEEPER_USER, settings.ZOOKEEPER_PASSWORD, all=True)
		dataJsonDict = {
			'SERVER_HOSTNAME': settings.SERVER_HOSTNAME,
			'SERVER_PORT': settings.SERVER_PORT,
			'CHILDREN': []
		}
		if self.connection.exists(path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID):
			self.connection.set(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID,
				value=json.JSONEncoder().encode(dataJsonDict).encode()
			)
		else:
			self.connection.create_async(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE + settings.ZOOKEEPER_NODE_ID,
				value=json.JSONEncoder().encode(dataJsonDict).encode(),
				ephemeral=settings.ZOOKEEPER_NODE_EPHIMERAL
			)
		if settings.ZOOKEEPER_PATH_TO_NODE != '':
			data, stat = self.connection.get(settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE)
			dataJsonDict = json.loads(data.decode("utf-8"))
			if settings.ZOOKEEPER_NODE_ID not in dataJsonDict['CHILDREN']:
				dataJsonDict['CHILDREN'].append(settings.ZOOKEEPER_NODE_ID)
			self.connection.set(
				path=settings.ZOOKEEPER_ROOT + settings.ZOOKEEPER_PATH_TO_NODE,
				value=json.JSONEncoder().encode(dataJsonDict).encode()
			)

	def __initStorageServiceWatches(self):
		# lists are supposed to be thread safe in python
		self.storageServicesList = []

		# Called immediately, and from then on
		@self.connection.ChildrenWatch(settings.ZOOKEEPER_ROOT + "StorageServices")
		def watch_children(children):
			self.storageServicesList = []
			print("Children are now: %s" % children)
			for child in children:
				self.storageServicesList.append(child)

	def __initAuthenticationServiceWatches(self):
		# lists are supposed to be thread safe in python
		self.authenticationServiceList = []

		# Called immediately, and from then on
		@self.connection.ChildrenWatch(settings.ZOOKEEPER_ROOT + "Auth")
		def watch_children(children):
			self.authenticationServiceList = []
			print("Children are now: %s" % children)
			for child in children:
				self.authenticationServiceList.append(child)

	def getAvailableFs(self): return self.storageServicesList

	def getZooConnection(self): return self.connection

	def getStatus(self):
		result = "{"
		try:
			rootChildren = self.connection.get_children(settings.ZOOKEEPER_ROOT)
			for child in rootChildren:
				data, stat = self.connection.get(settings.ZOOKEEPER_ROOT + child)
				result += '"' + child + '": ' + data.decode("utf-8") + ","
				try:
					grandchildren = self.connection.get_children(settings.ZOOKEEPER_ROOT + child)
					for grandchild in grandchildren:
						data, stat = self.connection.get(settings.ZOOKEEPER_ROOT + child + '/' + grandchild)
						result += '"' + grandchild + '": ' + data.decode("utf-8") + ","
					data, stat = self.connection.get(settings.ZOOKEEPER_ROOT + child + '/')
					dataJsonDict = json.loads(data.decode("utf-8"))
					dataJsonDict['CHILDREN'] = grandchildren
					self.connection.set(
						path=settings.ZOOKEEPER_ROOT + child,
						value=json.JSONEncoder().encode(dataJsonDict).encode()
					)
				except Exception:
					pass
			result = result[:-1] + '}'
			self.status = json.loads(result)
			self.initZkTree()
			return self.status
		except Exception:
			self.__zooConnect()
			return self.getStatus()

	def getNodeData(self, node):
		try:
			return self.status[node]
		except Exception:
			return {}

	def initZkTree(self):
		serviceData = self.getNodeData('WebService')
		self.webService = serviceData['SERVER_HOSTNAME'] + ':' + serviceData['SERVER_PORT'] + '/'

		serviceData = self.getNodeData('ApplicationService')
		self.applicationService = serviceData['SERVER_HOSTNAME'] + ':' + serviceData['SERVER_PORT'] + '/'

		serviceData = self.getNodeData('Auth')
		self.authenticationServiceList = []
		for authService in serviceData['CHILDREN']:
			authServiceData = self.getNodeData(authService)
			authServiceDict = {
				'name': authService,
				'url': authServiceData['SERVER_HOSTNAME'] + ':' + authServiceData['SERVER_PORT'] + '/'
			}
			self.storageServicesList.append(authServiceDict)

		serviceData = self.getNodeData('StorageServices')
		self.storageServicesList = []
		for storageService in serviceData['CHILDREN']:
			storageServiceData = self.getNodeData(storageService)
			storageServiceDict = {
				'name': storageService,
				'url': storageServiceData['SERVER_HOSTNAME'] + ':' + storageServiceData['SERVER_PORT'] + '/'
			}
			self.storageServicesList.append(storageServiceDict)

	def heartbeat(self):
		threading.Timer(300.0, self.heartbeat).start()
		print("Heartbeat")
		print(str(self.getStatus()))


zk = Zooconf()
