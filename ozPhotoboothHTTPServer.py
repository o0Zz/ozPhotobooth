import threading, logging, http.server, os, urllib.request, urllib.error, urllib.parse, zipstream, socketserver, traceback
import re, base64

logger = logging.getLogger(__name__) 
#https://gist.github.com/fxsjy/5465353

class ozHTTPServerRoute:
	def __init__(self, aPath, aFunction, afNeedAuth):
		self.mPath = aPath
		self.mFunction = aFunction
		self.mfNeedAuth = afNeedAuth

	def extractPath(self, anHTTPPath):
		if len(anHTTPPath) >= len(self.mPath) and anHTTPPath.startswith(self.mPath):
			return anHTTPPath[len(self.mPath):]

		return None

class ozPhotoboothHTTPServerHandler(http.server.BaseHTTPRequestHandler):
	def	__init__(self, request, client_address, server):

		self.ROUTES = [
			ozHTTPServerRoute("/info.json", 		ozPhotoboothHTTPServerHandler.serve_info, 				False),
			ozHTTPServerRoute("/photo", 			ozPhotoboothHTTPServerHandler.serve_photo, 				False),

			ozHTTPServerRoute("/admin/photos.zip", 	ozPhotoboothHTTPServerHandler.serve_admin_photo_zip, 	True),
			ozHTTPServerRoute("/admin/config.json", ozPhotoboothHTTPServerHandler.serve_admin_config, 		True),
			ozHTTPServerRoute("/admin", 			ozPhotoboothHTTPServerHandler.serve_admin, 				True),

			ozHTTPServerRoute("", 					ozPhotoboothHTTPServerHandler.serve_file, 				False) #Default route
		]

		http.server.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

	def do_HEAD(self):
		logger.debug("HEAD: " + self.path)
		self.send_error(501, 'Not implemented')

	def isAuthenticated(self):
		theAuth = self.headers['Authorization']
		if theAuth != None:
			theAuths = theAuth.split(" ")
			if len(theAuths) >= 2 and theAuths[0] == "Basic":
				theCredentials = base64.b64decode(bytes(theAuths[1], "utf-8"))
				theCredentials = theCredentials.decode("utf-8") .split(":")
				if theCredentials != None and len(theCredentials) >= 2:
					if self.server.isCredentialsValid(theCredentials[0], theCredentials[1]):
						return True

		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"ozHTTPSever\"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		self.send_string('<b>Not authenticated !</b>')
		return False

	def serve_info(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.send_string("{\"last_photo_id\": " + str(self.server.mPhotoDisk.GetNextPhotoID() - 1) + "}")

	def serve_admin_config(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.send_string(self.server.ToJSON())

	def serve_admin_photo_zip(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/zip')
		self.send_header('Content-Disposition', 'attachment; filename="photos.zip"')
		self.end_headers()

		#Problem zip: https://stackoverflow.com/questions/10405210/create-and-stream-a-large-archive-without-storing-it-in-memory-or-on-disk
		theZipStream = zipstream.ZipStream(self.server.mPhotoDisk.GetPhotoPath())
		for data in theZipStream:
			self.wfile.write(data)

	def serve_photo(self):
		self.send_file( self.server.mPhotoDisk.GetPhotoPath() + "/" + self.path )

	def serve_admin(self):
		self.send_file( self.server.mHTTPFolder + "/admin/" + self.path )

	def serve_file(self):
		self.send_file( self.server.mHTTPFolder + "/" + self.path )

	def send_string(self, aString):
		self.wfile.write(str(aString).encode("utf-8"))

	def send_file(self, aFullPath):
		if os.path.isdir(aFullPath):
			aFullPath = aFullPath + "/index.html"

		theExt = os.path.splitext(aFullPath)[-1]
		theMimetypes = {
			'.html': 'text/html',
			'.jpg':'image/jpeg',
			'.jpeg':'image/jpeg',
			'.gif': 'image/gif',
			'.js': 'application/javascript',
			'.css': 'text/css',
		}

		theMimeType = theMimetypes.get(theExt)
		if theMimeType is None:
			theMimeType = "application/octet-stream"
			
		if os.path.isfile(aFullPath):
			logger.debug("Serving: " + str(aFullPath))
			
			f = open(aFullPath, "rb")

			self.send_response(200)
			self.send_header('Content-type', theMimeType)
			self.end_headers()

			theData = f.read()

			self.wfile.write(theData)
			f.close()
		else:
			logger.error("404 File not found: " + str(aFullPath))
			self.send_error(404, 'File not found')
				
	def do_GET(self):

		logger.debug("GET: " + self.path)
		
		try:

			for theRoute in self.ROUTES:
				theNewPath = theRoute.extractPath(self.path)
				if theNewPath != None:

					if theRoute.mfNeedAuth and not self.isAuthenticated():
						return

					self.path = theNewPath
					
					theRoute.mFunction(self)
					break

		except Exception as e: 
			logger.error("EXCEPTION in do_GET: " + str(e))
			logger.error(traceback.format_exc())

		
# -----------------------------------------------------------------

class ozPhotoboothHTTServerClass(socketserver.ThreadingMixIn, http.server.HTTPServer):

	def __init__(self, *args, **kw):
		http.server.HTTPServer.__init__(self, *args, **kw)
		self.mfRunning = True

	def SetPhotoDisk(self, aPhotoDisk):
		self.mPhotoDisk = aPhotoDisk

	def SetHTTPFolder(self, anHTTPFolder):
		self.mHTTPFolder = anHTTPFolder

	def SetConfig(self, aConfig):
		self.mConfig = aConfig

	def isCredentialsValid(self, aLogin, aPassword):
		theLogin, thePassword = self.mConfig.GetHTTPCredentials()
		if aLogin == theLogin and aPassword == thePassword:
			return True

		logger.error("Invalid credentials: Login=" + str(aLogin) + " Password=" + str(aPassword))
		return False

	def serve_until_shutdown(self):
		while self.mfRunning:
			self.handle_request()

		self.server_close()
			
	def shutdown(self):
		self.mfRunning = False
		try:
			urllib.request.urlopen('http://%s:%s/' % ("127.0.0.1", self.server_port))
		except urllib.error.URLError:
			pass
			
		self.server_close()
		
# -----------------------------------------------------------------

class ozPhotoboothHTTPServer(threading.Thread):

	def __init__(self, aConfig, aPhotoDisk):
		threading.Thread.__init__(self)

		self.mConfig = aConfig
		self.mPhotoDisk = aPhotoDisk
		self.mHTTPFolder = self.mConfig.GetHTTPServerPath()
		
		self.Start()
		
	def Start(self):
		self.start()
	
	def Stop(self):
		logger.debug("Stopping HTTP Server...")
		self.mHTTPServer.shutdown()
		self.join(1.0)
		
	def run(self):
		
		self.mHTTPServer = ozPhotoboothHTTServerClass(self.mConfig.GetHTTPServerIPPort(), ozPhotoboothHTTPServerHandler)
		self.mHTTPServer.SetPhotoDisk(self.mPhotoDisk)
		self.mHTTPServer.SetHTTPFolder(self.mHTTPFolder)
		self.mHTTPServer.SetConfig(self.mConfig)

		logger.debug("HTTP Server running on: " + str(self.mConfig.GetHTTPServerIPPort()))
			
		self.mHTTPServer.serve_until_shutdown()
		
		