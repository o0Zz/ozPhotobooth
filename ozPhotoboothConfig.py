import logging, json, os, glob, shutil

import simplejson as simplejson

logger = logging.getLogger(__name__) 

class ozPhotoboothConfig:

	def __init__(self, aConfigPath):
		self.mConfig = None
		self.mConfigPath = aConfigPath

		logger.info("Loading configuration: " + str(self.mConfigPath) + " ...")

		if not self.Load(self.mConfigPath):
			if self.Load(self.mConfigPath + ".bak"):
				shutil.move(self.mConfigPath + ".bak", self.mConfigPath)

	def Load(self, aFilename):
		logger.debug("Trying to load " + str(aFilename) + "...")
		try:
			with open(aFilename, encoding='utf-8') as f:
				self.mConfig = json.load(f)
				return True

		except Exception as e:
			logger.error("Unable to load configuration file: " + str(aFilename))
			logger.error(e)

		return False

	def Save(self):
		logger.debug("Trying to save " + str(self.mConfigPath) + "...")
		shutil.move(self.mConfigPath, self.mConfigPath + ".bak")
		theConfigFD = open(self.mConfigPath, "w", encoding='utf-8')
		theConfigFD.write(simplejson.dumps(self.mConfig, indent=4))
		theConfigFD.close()
		return True

	def DetectScreenResolution(self):
		import tkinter as tk
		root = tk.Tk()
		return root.winfo_screenwidth(), root.winfo_screenheight()

	def isLoaded(self):
		return self.mConfig != None

	def GetScreenResolution(self):
		return self.Get("screen", "width", 640), self.Get("screen", "height", 480)
	
	def GetScreenCoordinate(self):
		return self.Get("screen", "x", 0), self.Get("screen", "y", 0)
			
	@staticmethod
	def LoadPreviewConfig(aFilename):
		theResult = None
		if aFilename != None:
			try:
				with open(aFilename) as f:
					theResult = json.load(f)
			except Exception as e: 
				logger.error("LoadPreviewConfig EXCEPTION: " + str(e))

		return theResult
		
	def GetResultPreview(self):
		return ozPhotoboothConfig.LoadPreviewConfig(self.Get("resultpreview", "file", None))
	
	def GetResultPreviewTimeMs(self):
		return self.Get("resultpreview", "time_ms", 5000)
	
	def GetPrintPreview(self):
		return ozPhotoboothConfig.LoadPreviewConfig(self.Get("printpreview", "file", None))

	def GetPrintPreviewTexts(self):
		return self.Get("printpreview", "texts", [])

	def IsPrintPreviewAutoGenerate(self):
		return self.Get("printpreview", "auto_generate", True)

	def GetPhotoPath(self):
		theSavePath = os.path.abspath(self.Get("takeshot", "photo_path"))
		logger.debug("Config save path: " + str(theSavePath))
		
		thePaths = glob.glob(theSavePath)
		if (len(thePaths) != 0):
			for thePath in thePaths:
				if os.access(str(thePath), os.W_OK):
					logger.info("Save path selected: " + str(thePath))
					return str(thePath)
				else:
					logger.error("Permission denied for path: " + str(thePath))

		logger.error("Unable to find a correct place to save photo, create ./photos/ and use it")
		thePath = str(os.path.abspath("./photos/"))
		if not os.path.isdir(thePath):
			os.mkdir(thePath)
		return thePath
		
	def GetShotCount(self):
		return self.Get("takeshot", "count")
		
	def GetIconShotDone(self):
		return self.Get("shot_icons", "done", None)
		
	def GetIconShotRemaining(self):
		return self.Get("shot_icons", "remaining", None)	
		
	def GetIconResolution(self):
		width = self.Get("shot_icons", "width", 0)
		height = self.Get("shot_icons", "height", 0)

		return int(width), int(height)
	
	def GetIconPositionY(self):
		y = self.Get("shot_icons", "y", 0)
		return int(y)
	
	def GetIconSpace(self):
		return self.Get("shot_icons", "space", 0)
		
	def GetCameraResolution(self):
		return self.Get("camera", "width", 1920), self.Get("camera", "height", 1080)
		
	def IsCameraNeedFlipVertically(self):
		return self.Get("camera", "flip_vertically", False)
		
	def IsCameraNeedFlipHorizontally(self):
		return self.Get("camera", "flip_horizontally", False)

	def GetCameraIndex(self):
		return int ( self.Get("camera", "index", 0) )
		
	def GetHTTPServerIPPort(self):
		return self.Get("httpserver", "ip", "0.0.0.0"), self.Get("httpserver", "port", 80)
	
	def GetHTTPServerPath(self):
		return self.Get("httpserver", "path", "./html/")
	
	def GetDNSServerIP(self):
		return self.Get("dnsserver", "ip", "")

	def GetHTTPCredentials(self):
		return self.Get("httpserver", "login", "admin"), self.Get("httpserver", "password", "12345678")

	def GetTextFont(self):
		return self.Get("text", "font", "DejaVuSans")
		
	def GetTextSize(self):
		return self.Get("text", "size", 100)
		
	def GetSoundShot(self):
		return self.Get("sound", "shot", None)
		
	def GetSoundCountdown(self):
		return self.Get("sound", "countdown", None)
		
	def GetSoundDryer(self):
		return self.Get("sound", "dryer", None)

	def GetTextColor(self):
		return self.Get("text", "color", "FFFFFF")
		
	def Get(self, aSection, aKey, aDefaultValue = None):
		if aSection in self.mConfig:
			if aKey in self.mConfig[aSection]:
				return self.mConfig[aSection][aKey]
		
		return aDefaultValue

	def Set(self, aSection, aKey, aValue):
		if not self.mConfig.has_key(aSection):
			self.mConfig[aSection] = {}

		self.mConfig[aSection][aKey] = aValue

	def ToJSON(self):
		return self.mConfig
