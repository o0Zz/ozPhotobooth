import logging, pygame

logger = logging.getLogger(__name__) 

class ozPhotoboothSound():
	Countdown 	= 0
	Shot 		= 1
	Dryer 		= 2
	
	SoundLogStr = ["Countdown", "Shot", "Dryer"]
	
	def __init__(self, aConfig):
		self.mSoundTable = [None, None, None]
		self.mConfig = aConfig

		pygame.mixer.init()

		if self.mConfig.GetSoundShot() != None:
			self.mSoundTable[ozPhotoboothSound.Shot] = pygame.mixer.Sound(self.mConfig.GetSoundShot())
		if self.mConfig.GetSoundCountdown() != None:
			self.mSoundTable[ozPhotoboothSound.Countdown] = pygame.mixer.Sound(self.mConfig.GetSoundCountdown())
		if self.mConfig.GetSoundDryer() != None:
			self.mSoundTable[ozPhotoboothSound.Dryer] = pygame.mixer.Sound(self.mConfig.GetSoundDryer())
	
	def Play(self, anIdx):
		if anIdx < len(self.mSoundTable) and self.mSoundTable[anIdx] != None:
			logger.info("Playing " + ozPhotoboothSound.SoundLogStr[anIdx] + " sound ...")
			self.mSoundTable[anIdx].play()
			
	def Stop(self, anIdx):
		if anIdx < len(self.mSoundTable) and self.mSoundTable[anIdx] != None:
			logger.info("Stopping " + ozPhotoboothSound.SoundLogStr[anIdx] + " sound ...")
			self.mSoundTable[anIdx].stop()
				