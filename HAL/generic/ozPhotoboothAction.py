import logging

logger = logging.getLogger(__name__) 

class ozPhotoboothAction:
	def __init__(self, aConfig):
		pass

	def Setup(self):
		return True

	def Start(self):
		pass

	def Stop(self):
		pass

	def SetButtonLed(self, afON):
		logger.info(("Enabling" if afON else "Disabling") + " button led ...")

	def SetLight(self, afON):
		logger.info(("Enabling" if afON else "Disabling") + " light ...")

