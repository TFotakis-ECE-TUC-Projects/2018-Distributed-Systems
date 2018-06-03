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
			'SHARED_KEY_BASE_64': settings.SHARED_KEY_BASE_64,
			'CHILDREN': []
		}
		if settings.ZOOKEEPER_PATH_TO_NODE == 'Auth/':
			dataJsonDict['AUTH_SYSTEM'] = settings.AUTH_SYSTEM
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
		self.storageServicesList = []

		@self.connection.ChildrenWatch(settings.ZOOKEEPER_ROOT + "StorageServices")
		def watch_children(children):
			print(self.readTree())
			if settings.ZOOKEEPER_PATH_TO_NODE == "StorageServices/":
				node = {
					'SERVER_HOSTNAME': settings.SERVER_HOSTNAME,
					'SERVER_PORT': settings.SERVER_PORT,
					'CHILDREN': []
				}
				if node not in self.storageServicesList:
					self.__publishService()

	def __initAuthenticationServiceWatches(self):
		self.authenticationServiceList = []

		@self.connection.ChildrenWatch(settings.ZOOKEEPER_ROOT + "Auth")
		def watch_children(children):
			print(self.readTree())
			if settings.ZOOKEEPER_PATH_TO_NODE == "Auth/":
				node = {
					'SERVER_HOSTNAME': settings.SERVER_HOSTNAME,
					'SERVER_PORT': settings.SERVER_PORT,
					'SHARED_KEY_BASE_64': settings.SHARED_KEY_BASE_64,
					'CHILDREN': [],
					'AUTH_SYSTEM': settings.AUTH_SYSTEM
				}
				if node not in self.authenticationServiceList:
					self.__publishService()

	def getAvailableFs(self): return self.storageServicesList

	def getZooConnection(self): return self.connection

	def readTree(self):
		result = "{"
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

	def getStatus(self):
		try:
			return self.readTree()
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
			if authServiceData != {}:
				baseUrl = authServiceData['SERVER_HOSTNAME'] + ((':' + authServiceData['SERVER_PORT']) if authServiceData['SERVER_PORT'] != '' else '') + '/'
				loginUrl = baseUrl + 'login?system=' + authServiceData['AUTH_SYSTEM'] + '&callback='
				registerUrl = baseUrl + 'register?system=' + authServiceData['AUTH_SYSTEM'] + '&callback='
				authServiceDict = {
					'name': authService,
					'url': baseUrl,
					'loginUrl': loginUrl,
					'registerUrl': registerUrl,
					'sharedKey': authServiceData['SHARED_KEY_BASE_64'],
					'system': authServiceData['AUTH_SYSTEM']
				}
				self.authenticationServiceList.append(authServiceDict)

		serviceData = self.getNodeData('StorageServices')
		self.storageServicesList = []
		for storageService in serviceData['CHILDREN']:
			storageServiceData = self.getNodeData(storageService)
			if storageServiceData != {}:
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
