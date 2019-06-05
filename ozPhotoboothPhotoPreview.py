#
#pip install opencv-python
#pip install Pillow
#

import logging, os, re, sys, random, cv2, numpy
import ozPhotoboothConfig
from PIL import Image

USE_PIL = False

if USE_PIL:
	from ozPhotoboothPhotoPreviewPIL import ozPhotoboothPhotoPreviewPIL as ozPhotoboothPhotoPreview
else:
	from ozPhotoboothPhotoPreviewOpenCV2 import ozPhotoboothPhotoPreviewOpenCV2 as ozPhotoboothPhotoPreview

logger = logging.getLogger(__name__) 
CONFIGURATION_FILENAME = "./ozPhotobooth.cfg"

# ================================================= 

def Usage(aRetCode):
	print ("Usage:")
	print ("      " + sys.argv[0] + " [Options]")
	print ("")
	print ("Options:")
	print ("      -photopath <path>      : Where are located all photos")
	print ("      -preview <preview.cfg> : Preview to use")
	print ("      -debug                 : Enable debug mode in order to debug .cfg")
	print ("")
	print ("i.e:")
	print ("      " + sys.argv[0] + " -photopath /d/media/pi/AAAA -preview ./res/result.cfg -debug")
	print ("      " + sys.argv[0] + " -photopath /d/media/pi/AAAA -preview ./res/printpreview.cfg -debug")
	print ("")
	sys.exit(aRetCode)
			
# ================================================= 

def Show(aPreview, afRefreshOnFly = False, aPreviewConfigPath = None):
	theWindowName = "ImageResultShow"
	cv2.imshow(theWindowName, numpy.array(aPreview.BuildImage()))
		
	while cv2.getWindowProperty(theWindowName, 0) >= 0:
	
		keyCode = cv2.waitKey(50)
		if keyCode != -1:
			break
			
		if afRefreshOnFly:
			aPreview.SetPreviewConfig(ozPhotoboothConfig.ozPhotoboothConfig.LoadPreviewConfig(aPreviewConfigPath))
			cv2.imshow(theWindowName, numpy.array(aPreview.BuildImage().convert('RGB'))[...,::-1])

	cv2.destroyAllWindows()

# ================================================= 

_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]   

# ================================================= 

if __name__ == '__main__':
	
	#logger.basicConfig(filename='ozPhotobooth.log', level=logger.DEBUG, format='%(asctime)s %(module)s: %(levelname)-8s %(message)s')
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(module)35s: %(levelname)-8s %(message)s')

	thePhotoPath = None
	thePreviewConfigPath = None
	thefDebug = False
	
	i = 1
	while i < len(sys.argv):
		if sys.argv[i] == "-photopath" and (i+1 < len(sys.argv)):
			i = i + 1
			thePhotoPath = sys.argv[i]
		elif sys.argv[i] == "-preview" and (i+1 < len(sys.argv)):
			i = i + 1
			thePreviewConfigPath = sys.argv[i]
		elif sys.argv[i] == "-debug":
			thefDebug = True
		else:
			print ("ERROR: Invalid parameters: " + sys.argv[i])
			Usage(1)
			
		i = i + 1
	
	if thePhotoPath == None:
		print ("ERROR: Missing parameter: -photopath")
		Usage(1)
		
	if thePreviewConfigPath == None:
		print ("ERROR: Missing parameter: -preview")
		Usage(1)
		
	theConfig = ozPhotoboothConfig.ozPhotoboothConfig(CONFIGURATION_FILENAME)
	if not theConfig.isLoaded():
		logger.error("Unable to load configuration: " + str(CONFIGURATION_FILENAME))
		sys.exit(1)

	theOutputFolder = os.path.join(thePhotoPath, "output")
	if not os.path.exists(theOutputFolder):
		os.mkdir(theOutputFolder)
	
	theFileList = [f for f in os.listdir(thePhotoPath) if os.path.isfile(os.path.join(thePhotoPath, f))]
	theFileList.sort(key=natural_sort_key)
	theNumberOfPhoto = theConfig.GetShotCount()

	i = 0
	while i + theNumberOfPhoto <= len(theFileList):
		thePreview = ozPhotoboothPhotoPreview(theConfig, ozPhotoboothConfig.ozPhotoboothConfig.LoadPreviewConfig(thePreviewConfigPath))
		
		for k in range (0, theNumberOfPhoto):
			thePreview.AddPhotoPath(os.path.join(thePhotoPath, theFileList[i + k]))

		thePreview.Save( os.path.join(theOutputFolder, theFileList[i] + ".jpg") )	
		logger.debug ("Percentage: " + str(int(i*100/len(theFileList))) + " %")
				
		i = i + theNumberOfPhoto
		
		if thefDebug:
			Show(thePreview, True, thePreviewConfigPath)
			break
	
	