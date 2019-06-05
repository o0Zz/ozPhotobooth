import logging, os, re, sys, random, time
from PIL import Image

logger = logging.getLogger(__name__) 

class ozPhotoboothPhotoPreviewBase():

	def __init__(self, aConfig, aPreviewDict):
		self.mConfig = aConfig
		self.mPhotoList = []
		self.mTextList = []
		self.SetPreviewConfig(aPreviewDict)
		
	def SetPreviewConfig(self, aPreviewDict):
		self.mPreviewDict = aPreviewDict
		self.mBackground = self.LoadImage(self.mPreviewDict["background"])

	def LoadImage(self, aPath):
		if Image.open(aPath).mode == "CMYK":
			logger.error("************** Unsupported 'CMYK' image format /!\\ Result will have wrong colors /!\\")
			logger.error("************** Please convert your image: '" + aPath + "' to RGB (open with mspaint.exe and save as ...)")

		return self._LoadImage(aPath)

	def AddPhotoPath(self, aPhotoPath):
		self.mPhotoList.append( self.LoadImage(aPhotoPath) )

	def AddTexts(self, aTexts):
		for theText in aTexts:
			self.AddText(theText)

	def AddText(self, aText):
		self.mTextList.append( aText )
		
	def BuildImage(self, aDstResolution = None, aProgressiveAlphaCallback = None):
		theResultPicture = self.Resize(self.mBackground, self.mPreviewDict["background_width"], self.mPreviewDict["background_height"])

		for i in range (0, len(self.mPreviewDict["position_photo"])):
			
			thePhotoPosition = self.mPreviewDict["position_photo"][i]
			if i < len(self.mPhotoList):
				thePhoto = self.mPhotoList[i]
			else:
				thePhoto = self.mPhotoList[random.randint(0, len(self.mPhotoList) - 1)] #Random photo

			thePhoto = self.Resize(thePhoto, thePhotoPosition["width"], thePhotoPosition["height"])
			
			if aProgressiveAlphaCallback != None:
				
				theResultPictureTmp = theResultPicture.copy()
				
				for k in range (0, 100, 10):
					thePhotoTmp = self.SetTransparency(thePhoto, k)
					
					thePhotoTmp = self.Rotate(thePhotoTmp, thePhotoPosition["rotation"])

					theResultPictureTmp = self.Blit(theResultPictureTmp, thePhotoTmp, thePhotoPosition["x"], thePhotoPosition["y"])

					if aDstResolution != None:
						logger.debug("Resize to Dst resolution Width: " + str(aDstResolution[0]) + " Height: " + str(aDstResolution[1]))
						theResultPictureTmp = self.Resize(theResultPictureTmp, aDstResolution[0], aDstResolution[1])
					
					aProgressiveAlphaCallback(self.ConvertToPILImg(theResultPictureTmp))

			thePhoto = self.Rotate(thePhoto, thePhotoPosition["rotation"])

			theResultPicture = self.Blit(theResultPicture, thePhoto, thePhotoPosition["x"], thePhotoPosition["y"])

		if aDstResolution != None:
			logger.debug("Resize to Dst resolution Width: " + str(aDstResolution[0]) + " Height: " + str(aDstResolution[1]))
			theResultPicture = self.Resize(theResultPicture, aDstResolution[0], aDstResolution[1])

		return self.ConvertToPILImg(theResultPicture)
	
	def Save(self, aDstFilename, aDPI = None): #aDPI=(300, 300)
		theResultPicture = self.BuildImage()
	
		if aDPI == None:
			theImgBackground = Image.open(self.mPreviewDict["background"])
			aDPI = theImgBackground.info['dpi']

		theFullPath = os.path.abspath(aDstFilename)
		theFolderPath = os.path.dirname(theFullPath)
		
		if not os.path.exists(theFolderPath):
			os.makedirs(theFolderPath)
			
		logger.info("Saving picture in: " + str(theFullPath))
		theResultPicture = theResultPicture.convert('RGB')

		theResultPicture.save(theFullPath, dpi=aDPI, icc_profile=theImgBackground.info.get('icc_profile'))
