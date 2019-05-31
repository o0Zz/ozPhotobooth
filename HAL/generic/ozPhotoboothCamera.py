import time, os, threading, logging, traceback
import pygame, pygame.camera
from PIL import Image, ImageDraw, ImageFont
from HAL import ozPhotoboothCameraBase

logger = logging.getLogger(__name__) 

NOSIGNAL_FILENAME = "./res/nosignal.jpg"

# ================================================= 
	
def IsWindowsPlatform():
	return os.name == 'nt' #posix

# ================================================= 
		
class ozPhotoboothCamera(ozPhotoboothCameraBase.ozPhotoboothCameraBase, threading.Thread):
	def __init__(self, aConfig):
		threading.Thread.__init__(self)
		ozPhotoboothCameraBase.ozPhotoboothCameraBase.__init__(self, aConfig)

		self.mLock = threading.Lock()
		self.mDisplay = None
		self.mPhoto = None
		self.mCamera = None
		self.mConfig = aConfig
		self.mfPreview = False
		self.mfRunning = False

	def Setup(self):
		logger.info("Looking for a camera...")

		pygame.init()
		pygame.display.set_caption("ozPhotobooth")
		pygame.display.set_icon(pygame.image.load("./res/icon.png"))

		theCameraIdx = self.mConfig.GetCameraIndex()
		theCameraResolution = self.mConfig.GetCameraResolution()
		theScreenResolution = self.mConfig.GetScreenResolution()

		#Because of an issue in pygame while writing this script, it's not possible to start camera on windows
		#This issue will be probably be fixed by the communauty soon, let see.
		if not IsWindowsPlatform():
			pygame.camera.init()
			theCameraList = pygame.camera.list_cameras()
			if len(theCameraList) == 0:
				logger.error( "Camera not found ! (Did you enabled v4l ?)" )
				logger.error( "$sudo sh -c echo 'bcm2835-v4l2' >> /etc/modules-load.d/modules.conf" )
				return False

			logger.info("Number of camera found: " + str(len(theCameraList)))
			logger.info("Selecting camera: " + str(theCameraIdx))

			if theCameraIdx >= len(theCameraList):
				logger.error("Camera index out of range !")
				return False

			self.mCamera = pygame.camera.Camera(theCameraList[theCameraIdx], theCameraResolution)
			logger.debug("Camera resolution: "  + str(theCameraResolution[0]) + "x" + str(theCameraResolution[1]))

		self.mDisplay = pygame.display.set_mode(theScreenResolution, 0)

		return ozPhotoboothCameraBase.ozPhotoboothCameraBase.Setup(self)
		
	def Start(self):
		if self.mCamera != None:
			self.mCamera.start()
			
		self.mfRunning = True
		self.start()
			
	def Stop(self):
		if self.mfRunning:
			self.mfRunning = False
			self.join()
		
		if self.mCamera != None:
			self.mCamera.stop()

		logger.debug("Exiting pygame ...")
		pygame.quit()

	def OnOverlayUpdated(self, anOverlayImg):
		theSurface = pygame.image.fromstring(anOverlayImg.tobytes(), anOverlayImg.size, anOverlayImg.mode)
		theOverlay = pygame.transform.scale(theSurface, self.mConfig.GetScreenResolution())
		with self.mLock:
			self.mOverlay = theOverlay

	def Capture(self, aFilename):
		thePhoto = None

		with self.mLock:
			thePhoto = self.mPhoto

		logger.info("Saving picture in: " + str(aFilename))
		pygame.image.save(thePhoto, aFilename)

	def StartPreview(self):
		self.mfPreview = True
		
	def StopPreview(self):
		self.mfPreview = False

	# Use 2 layer and display on over the second etc ...
	def run(self):
		logger.info("Camera running...")
			
		while self.mfRunning:
			try:
				with self.mLock:

					if self.mCamera != None:
						self.mPhoto = self.mCamera.get_image()
					else:
						self.mPhoto = pygame.image.load(NOSIGNAL_FILENAME)
						self.mPhoto = pygame.transform.scale(self.mPhoto, self.mConfig.GetCameraResolution())

					theDisplayImage = self.mPhoto

					if (self.mConfig.IsCameraNeedFlipVertically() or self.mConfig.IsCameraNeedFlipHorizontally()):
						theDisplayImage = pygame.transform.flip(theDisplayImage, self.mConfig.IsCameraNeedFlipVertically(), self.mConfig.IsCameraNeedFlipHorizontally())

					if (self.mConfig.GetCameraResolution() != self.mConfig.GetScreenResolution()): #Need to scale to screen size
						theDisplayImage = pygame.transform.scale(theDisplayImage, self.mConfig.GetScreenResolution())

					self.mDisplay.blit(theDisplayImage, (0,0))

					if self.mOverlay != None:
						self.mDisplay.blit(self.mOverlay, (0,0))

					#Update screen
				pygame.display.update()

				#Avoid infinite loop and 100% CPU Usage on windows
				time.sleep(0.1)

			except Exception as e:
				logger.error("PhotoboothCamera exeception: " + str(traceback.format_exc()))
				self.mfRunning = False
		
