import logging
import picamera
from HAL import ozPhotoboothCameraBase
import pygame

logger = logging.getLogger(__name__) 

# ================================================= 

class ozPhotoboothCamera(ozPhotoboothCameraBase.ozPhotoboothCameraBase):
	def __init__(self, aConfig):
		ozPhotoboothCameraBase.ozPhotoboothCameraBase.__init__(self, aConfig)

		self.mCamera = None
		self.mIconList = []
		self.mIconPosition = []
		self.mText = None
		self.mConfig = aConfig
		self.mfPreview = False
		self.mFont = None
		self.mOverlay = None
		self.mCurrentOverlayLayer = 3
		
	def Setup(self):
		logger.info("Looking for a camera...")
		
		theInitSuccessCount, theInitFailCount = pygame.init()
		if theInitFailCount > 0:
			logger.error("pygame init failed to load some modules: " + str(theInitFailCount))
		else:
			logger.info("pygame init success !")
		
		self.mDisplay = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		pygame.mouse.set_visible(False)
			  
		self.mCamera = picamera.PiCamera(resolution=picamera.PiCamera.MAX_RESOLUTION)
		try:
			self.mCamera.resolution = self.mConfig.GetCameraResolution()
		except:
			logger.warning("Camera resolution too high: " + str(self.mConfig.GetCameraResolution()) +  " - Max: " + str(self.mCamera.resolution) + "")
			#return False
			
		self.mCamera.framerate = 18
		logger.debug("Camera resolution: "  + str(self.mCamera.resolution[0]) + "x" + str(self.mCamera.resolution[1]))
		
		return ozPhotoboothCameraBase.ozPhotoboothCameraBase.Setup(self)
   
	def _RemoveOverlay(self):
		if self.mOverlay != None:
			self.mCamera.remove_overlay(self.mOverlay)
			self.mOverlay = None
			
	def _BlitImgPygame(self, anOverlayImg):
		theSurface = pygame.image.fromstring(anOverlayImg.tobytes(), anOverlayImg.size, anOverlayImg.mode)
		theOverlay = pygame.transform.scale(theSurface, self.mConfig.GetScreenResolution())
		self.mDisplay.blit(theOverlay, (0,0))
		pygame.display.update()
			
	def Start(self):			
		self.mfRunning = True
			
	def Stop(self):
		self.mfRunning = False
		self._RemoveOverlay()
		self.mCamera.close()
		
	def OnOverlayUpdated(self, anOverlayImg):
		if self.mfPreview == False:
			self._BlitImgPygame(anOverlayImg)
		else:			 
			#https://github.com/waveform80/picamera/issues/448
			#https://github.com/waveform80/picamera/issues/235
			theTmpOverlay = self.mCamera.add_overlay(anOverlayImg.tobytes(), size=anOverlayImg.size, layer=self.mCurrentOverlayLayer, fullscreen = False)
			theTmpOverlay.window = (self.mConfig.GetScreenCoordinate()[0], self.mConfig.GetScreenCoordinate()[1], self.mConfig.GetScreenResolution()[0], self.mConfig.GetScreenResolution()[1])
	
			self.mCurrentOverlayLayer = self.mCurrentOverlayLayer + 1
			if self.mCurrentOverlayLayer > 4:
				self.mCurrentOverlayLayer = 3
			
			self._RemoveOverlay()
			self.mOverlay = theTmpOverlay
			
	def GetOverlayResolution(self):
		theResolution = self.mConfig.GetScreenResolution()
		
		# Create an image padded to the required size with mode 'RGBA' (Must be a multiple of 32 and 16 - See doc)
		theLayerW = ((theResolution[0] + 31) // 32) * 32
		theLayerH = ((theResolution[1] + 15) // 16) * 16
		return theLayerW, theLayerH

	def Capture(self, aFilename):
		logger.info("Saving picture in: " + str(aFilename))
		self.mCamera.capture(aFilename)

	def StartPreview(self):
		self.mfPreview = True
		self._BlitImgPygame(self.GetBlackPicture())
		if self.mCamera != None:
			thePreview = self.mCamera.start_preview(resolution=self.mConfig.GetScreenResolution(), fullscreen=False)
			thePreview.window = (self.mConfig.GetScreenCoordinate()[0], self.mConfig.GetScreenCoordinate()[1], self.mConfig.GetScreenResolution()[0], self.mConfig.GetScreenResolution()[1])

	def StopPreview(self):
		self.mfPreview = False
		self._RemoveOverlay()
		if self.mCamera != None:
			self.mCamera.stop_preview()
