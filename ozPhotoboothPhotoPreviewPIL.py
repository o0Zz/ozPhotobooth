#
#pip install opencv-python
#pip install Pillow
#

import logging, os, re, sys, random, time
from PIL import Image
from PIL import PILLOW_VERSION

import ozPhotoboothPhotoPreviewBase

logger = logging.getLogger(__name__) 

class ozPhotoboothPhotoPreviewPIL(ozPhotoboothPhotoPreviewBase.ozPhotoboothPhotoPreviewBase):

	def __init__(self, aConfig, aPreviewDict):
		ozPhotoboothPhotoPreviewBase.ozPhotoboothPhotoPreviewBase.__init__(self, aConfig, aPreviewDict)
		logger.debug("Using PIL Version: {}".format(PILLOW_VERSION))
		
	def LoadImage(self, aPhotoPath):
		logger.debug("Loading image: " + aPhotoPath)
		theImg = Image.open(aPhotoPath)
		return theImg.convert('RGBA')
		
	def Rotate(self, aPhoto, aRotationDegree, aRGBBackground = (255, 255, 255)):
		return aPhoto.rotate(aRotationDegree, resample=Image.NEAREST, expand=True) #Image.NEAREST Image.BILINEAR Image.BICUBIC
	
	def Resize(self, aPhoto, aWidth, aHeight):
		return aPhoto.resize((int(aWidth), int(aHeight)), Image.HAMMING)

	def Blit(self, aPhotoSurface, aPhotoToBlit, x, y):
		width, height = aPhotoToBlit.size
		x = int(x-(width/2))
		y = int(y-(height/2))
		logger.debug("Blit Image (w={}, h={}) in x:{} y:{} of surface (w={}, h={})".format(width, height, x, y, aPhotoSurface.size[0], aPhotoSurface.size[1]))
		
		if x < 0 or y < 0:
			logger.error("ERROR: Unable to blit surface, X or Y is negative !")
			return aPhotoSurface
			
			#aPhotoSurface.paste(aPhotoToBlit, (int(x-(width/2)), int(y-(height/2))), aPhotoToBlit) #alpha composite don't know how to place image with negative coordinate
		aPhotoSurface.alpha_composite(aPhotoToBlit, (x, y))
		
		return aPhotoSurface

	def SetTransparency(self, aPhoto, aTransparencyPercentage):
		thePhotoTmp = aPhoto.copy()
		thePhotoTmp.putalpha(int(255*aTransparencyPercentage/100))
		return thePhotoTmp
		
	def ConvertToPILImg(self, aPhoto):
		return aPhoto
	
