import logging, os, re

logger = logging.getLogger(__name__) 

class ozPhotoboothPhotoDisk():

	def __init__(self, aConfig):
		self.mConfig = aConfig
		
		self.mPhotoPath = self.mConfig.GetPhotoPath()
		
		theFileList = [f for f in os.listdir(self.mPhotoPath) if os.path.isfile(os.path.join(self.mPhotoPath, f))]
		
		self.mNextPhotoID = 0
		if len(theFileList) > 0:
			self.mNextPhotoID = ozPhotoboothPhotoDisk._extract_filename_number(max(theFileList, key=ozPhotoboothPhotoDisk._extract_filename_number))
			
		self.mNextPhotoID = self.mNextPhotoID + 1
		logger.info("Next photo number = " + str(self.mNextPhotoID))
	
	@staticmethod
	def _extract_filename_number(f):
		theFilenameWithoutExt = os.path.splitext(f)[0]
		s = re.findall("\d+$", theFilenameWithoutExt)
		if len(s) > 0:
			return int(s[0])
		
		return -1
	
	def GetPhotoPath(self):
		return self.mPhotoPath
		
	def GetNextPhotoID(self):
		return self.mNextPhotoID
		
	def GetNextPhotoFilename(self):
		thePhotoFilename = os.path.join(self.mPhotoPath, str(self.mNextPhotoID) + ".jpg")
		self.mNextPhotoID = self.mNextPhotoID + 1
		return thePhotoFilename
