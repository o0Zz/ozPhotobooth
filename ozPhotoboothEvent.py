
class ozPhotoboothEvent:
	Unknown 		= 0
	PictureButton 	= 1
	ExitButton		= 0xFF

	def __init__(self, aType, aValue = None):
		self.type = aType
		self.value = aValue