import threading, logging, time, os
import ozPhotoboothPhotoPreviewPIL, ozPhotoboothPhotoPreviewOpenCV2, ozPhotoboothSound

logger = logging.getLogger(__name__) 
	
class ozPhotoboothSequence(threading.Thread):

	def __init__(self, aConfig, aCamera, anAction, aSound, aPhotoDisk):
		threading.Thread.__init__(self)

		logger.debug("Loading new sequencer ...")
		
		self.mConfig = aConfig
		self.mCamera = aCamera
		self.mAction = anAction
		self.mSound = aSound
		self.mPhotoDisk = aPhotoDisk
		self.mfRunning = False
		self.mfDone = False
		
		self.mFinalPreview = ozPhotoboothPhotoPreviewPIL.ozPhotoboothPhotoPreviewPIL(self.mConfig, self.mConfig.GetResultPreview())

		if self.mConfig.IsPrintPreviewAutoGenerate():
			self.mPrintPreview = ozPhotoboothPhotoPreviewOpenCV2.ozPhotoboothPhotoPreviewOpenCV2(self.mConfig, self.mConfig.GetPrintPreview())
		
	def Start(self):
		self.mfRunning = True
		self.start()
	
	def Stop(self):
		self.mfRunning = False
		self.join()
	
	def IsRunning(self):
		return self.mfRunning
		
	def IsDone(self):
		return self.mfDone
		
	def run(self):
		logger.info("Sequence started ...")

		self.mCamera.SetText(self.mConfig.Get("takeshot", "ready", "Ready ?"))
		self.mAction.SetLight(True)

		for k in range (0, self.mConfig.GetShotCount()):

			self.mCamera.SetPicture(None)

			time.sleep(float(self.mConfig.Get("takeshot", "interval_ms"))/1000) #Wait 1s between 2 pictures
			
			if not self.mConfig.Get("takeshot", "burst") or k == 0:
			
				for i in range (self.mConfig.Get("takeshot", "countdown"), 0, -1):
					self.mCamera.SetText(str(i))
					self.mSound.Play(ozPhotoboothSound.ozPhotoboothSound.Countdown)
					self.mAction.SetButtonLed(True)
					time.sleep(0.2)
					self.mAction.SetButtonLed(False)
					
					time.sleep(0.8)
					if not self.mfRunning:
						return
						
			self.mSound.Play(ozPhotoboothSound.ozPhotoboothSound.Shot)
			self.mCamera.SetText(None)

			thePhotoFilename = self.mPhotoDisk.GetNextPhotoFilename()

			self.mCamera.LockOverlayUpdate()
			self.mCamera.DisplayIcons(k + 1)
			self.mCamera.SetPicture(self.mCamera.GetBlackPicture())
			self.mCamera.UnlockOverlayUpdate()

			thePhoto = self.mCamera.Capture(thePhotoFilename)
			
			self.mFinalPreview.AddPhotoPath( thePhotoFilename )

			if self.mConfig.IsPrintPreviewAutoGenerate():
				self.mPrintPreview.AddPhotoPath( thePhotoFilename )
			
		self.mAction.SetLight(False)
		self.mCamera.StopPreview()

		self.mSound.Play(ozPhotoboothSound.ozPhotoboothSound.Dryer)
		
			#Result
		theResultPicture = self.mFinalPreview.BuildImage(self.mCamera.GetOverlayResolution(), self.mCamera.SetPicture)
		self.mCamera.SetPicture(theResultPicture)

		if self.mConfig.IsPrintPreviewAutoGenerate():
			self.mPrintPreview.AddTexts(self.mConfig.GetPrintPreviewTexts())
			self.mPrintPreview.Save(os.path.join( os.path.dirname(thePhotoFilename), "final", os.path.basename(thePhotoFilename)))
		
		time.sleep(self.mConfig.GetResultPreviewTimeMs() / 1000)

		self.mCamera.DisplayIcons(0)
		self.mCamera.SetPicture(None)
		self.mCamera.StartPreview()
		
		self.mfRunning = False
		self.mfDone = True
