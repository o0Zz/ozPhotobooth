#
#pip install opencv-python
#

import logging, os, re, sys, random, cv2, time
from PIL import Image
import ozPhotoboothPhotoPreviewBase

logger = logging.getLogger(__name__) 

class ozPhotoboothPhotoPreviewOpenCV2(ozPhotoboothPhotoPreviewBase.ozPhotoboothPhotoPreviewBase):

	def __init__(self, aConfig, aPreviewDict):
		ozPhotoboothPhotoPreviewBase.ozPhotoboothPhotoPreviewBase.__init__(self, aConfig, aPreviewDict)

	def LoadImage(self, aPhotoPath):
		logger.debug("Loading image: " + aPhotoPath)
		thePhoto = cv2.imread(aPhotoPath)
		thePhoto = cv2.cvtColor( thePhoto, cv2.COLOR_BGR2RGBA )
		return thePhoto
		
	def Rotate(self, aPhoto, aRotationDegree, aRGBBackground = (255, 255, 255)):
		height, width = aPhoto.shape[:2]
		width_big = width*2
		height_big = height*2

		thePhoto = cv2.resize(aPhoto, (width_big, height_big), interpolation = cv2.INTER_CUBIC)
		thePhoto = cv2.warpAffine(thePhoto, cv2.getRotationMatrix2D((width_big/2, height_big/2), aRotationDegree, 0.5), (width_big,height_big), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=aRGBBackground)
		return thePhoto
	
	def Resize(self, aPhoto, aWidth, aHeight):
		return cv2.resize(aPhoto, (int(aWidth), int(aHeight)), interpolation = cv2.INTER_CUBIC)

	def Blit(self, aPhotoSurface, aPhotoToBlit, x, y):
		image_height, image_width = aPhotoToBlit.shape[:2]
		surface_height, surface_width = aPhotoSurface.shape[:2]
		
		surface_y1 = int(y) - int(image_height/2)
		surface_y2 = int(y) + int(image_height/2)
		surface_x1 = int(x) - int(image_width/2)
		surface_x2 = int(x) + int(image_width/2)

		image_y1 = 0
		image_x1 = 0
		image_y2 = image_height
		image_x2 = image_width
		
		if surface_y2 > surface_height:
			surface_y2 = surface_height
			image_y2 = surface_height - surface_y1
		
		if surface_y1 < 0:
			image_y1 += -(surface_y1)
			surface_y1 = 0
			
		if surface_x2 > surface_width:
			surface_x2 = surface_width
			image_x2 = surface_width - surface_x1
			
		if surface_x1 < 0:
			image_x1 += -(surface_x1)
			surface_x1 = 0
			
		if (image_x2-image_x1 != surface_x2-surface_x1):
			logger.error("ERROR: Surface width size (" + str(surface_x1) + "-" + str(surface_x2) + ") != Photo width size (" + str(image_x1) + "-" + str(image_x2) + ")")
			return None
			
		if (image_y2-image_y1 != surface_y2-surface_y1):
			logger.error("ERROR: Surface height size (" + str(surface_y1) + "-" + str(surface_y2) + ") != Photo height size (" + str(image_y1) + "-" + str(image_y2) + ")")
			return None
			
		# logger.debug("Surface Size:  " + str(surface_height) + "x" + str(surface_width) )
		# logger.debug("Surface Pos:   Y=" + str(surface_y1) + "-" + str(surface_y2) + " X=" + str(surface_x1) + "-" + str(surface_x2) )
		# logger.debug("Image Size:    " + str(image_height) + "x" + str(image_width) )
		# logger.debug("Image Pos:     Y=" + str(image_y1) + "-" + str(image_y2) + " X=" + str(image_x1) + "-" + str(image_x2) )

		alpha_s = aPhotoToBlit[image_y1:image_y2, image_x1:image_x2, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(0, 3):
			aPhotoSurface[surface_y1:surface_y2, surface_x1:surface_x2, c] = (alpha_s * aPhotoToBlit[image_y1:image_y2, image_x1:image_x2, c] + alpha_l * aPhotoSurface[surface_y1:surface_y2, surface_x1:surface_x2, c])
		
		return aPhotoSurface
		
	def SetTransparency(self, aPhoto, aTransparencyPercentage):
		thePhotoTmp = aPhoto.copy()
		thePhotoTmp[:, :, 3] = aTransparencyPercentage
		return thePhotoTmp
		
	def ConvertToPILImg(self, aPhoto):
		return Image.fromarray(aPhoto)