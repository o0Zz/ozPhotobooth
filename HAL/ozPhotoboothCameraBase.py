import time, os, logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

NOSIGNAL_FILENAME = "./res/nosignal.jpg"

# =================================================

def IsWindowsPlatform():
    return os.name == 'nt'  # posix

# =================================================

class ozPhotoboothCameraBase():
    def __init__(self, aConfig):
        self.mIconPosition = []
        self.mText = None
        self.mPicture = None
        self.mConfig = aConfig
        self.mFont = None
        self.mFontColor = None
        self.mBlackOverlay = None
        self.mOverlayUpdateLocked = False
        self.mDisplayIconsCount = 0

    def Setup(self):
        logger.info("Looking for a camera...")

        theCameraIdx = self.mConfig.GetCameraIndex()
        theLayerW, theLayerH = self.GetOverlayResolution()
        
        theScreenResolution = self.mConfig.GetScreenResolution()
        logger.debug("Screen resolution: " + str(theScreenResolution[0]) + "x" + str(theScreenResolution[1]))

        #Setup black overlay
        self.mBlackOverlay = Image.new('RGBA', self.GetOverlayResolution())
        theDraw = ImageDraw.Draw(self.mBlackOverlay)
        theDraw.rectangle([(0, 0), self.mBlackOverlay.size], fill=(0, 0, 0))

        self.mFontColor = tuple(int(self.mConfig.GetTextColor()[i:i + 2], 16) for i in (0, 2, 4))
        try:
            self.mFont = ImageFont.truetype(self.mConfig.GetTextFont(), self.mConfig.GetTextSize())
        except:
            try:
                logger.warning("ozPhotoboothCameraBase Unable to load font: " + self.mConfig.GetTextFont() + ", Trying to load Arial...")
                self.mFont = ImageFont.truetype("arial.ttf", self.mConfig.GetTextSize())
            except:
                logger.error("ozPhotoboothCameraBase Unable to load fonts !")
                return False

        self.mIconOn = Image.open(self.mConfig.GetIconShotDone())
        self.mIconOn = self.mIconOn.resize(self.mConfig.GetIconResolution(), Image.ANTIALIAS)

        self.mIconOff = Image.open(self.mConfig.GetIconShotRemaining())
        self.mIconOff = self.mIconOff.resize(self.mConfig.GetIconResolution(), Image.ANTIALIAS)

        theCenterWidth = theLayerW/ 2
        theIconWidth = self.mConfig.GetIconResolution()[0]
        theShotCount = self.mConfig.GetShotCount()
        theShotXBegin = theCenterWidth - (((theIconWidth * theShotCount) + (self.mConfig.GetIconSpace() * (theShotCount-1))) / 2)

        for i in range(0, theShotCount):
            y = int(self.mConfig.GetIconPositionY())
            x = int(theShotXBegin + (i * (theIconWidth + self.mConfig.GetIconSpace())))
            self.mIconPosition.append((x, y))

        logger.debug("ozPhotoboothCamera Setup done !")

        self.UpdateOverlay()

        return True

    def LockOverlayUpdate(self):
        self.mOverlayUpdateLocked = True

    def UnlockOverlayUpdate(self):
        self.mOverlayUpdateLocked = False
        self.UpdateOverlay()

    def GetOverlayResolution(self):
        return self.mConfig.GetScreenResolution()

    def OnOverlayUpdated(self):
        raise NotImplemented

    def UpdateOverlay(self):
        if self.mOverlayUpdateLocked:
            return

        theLayerW, theLayerH = self.GetOverlayResolution()

        # Create an image padded to the required size with mode 'RGBA' (Must be a multiple of 32 and 16 - See doc)
        theOverlayImg = Image.new('RGBA', (theLayerW, theLayerH))

        if self.mPicture != None:
            theOverlayImg.paste(self.mPicture, (0, 0), self.mPicture)
        else:
            if self.mText != None:
                theDraw = ImageDraw.Draw(theOverlayImg)
                theFontW, theFontH = theDraw.textsize(self.mText, font=self.mFont)
                theDraw.text(((theLayerW - theFontW) / 2, (theLayerH - theFontH) / 2), self.mText, self.mFontColor, font=self.mFont)

            if self.mDisplayIconsCount != None:
                for i in range(0, self.mConfig.GetShotCount()):
                    if i < self.mDisplayIconsCount:
                        theOverlayImg.paste(self.mIconOn, self.mIconPosition[i], self.mIconOn)
                    else:
                        theOverlayImg.paste(self.mIconOff, self.mIconPosition[i], self.mIconOff)

        self.OnOverlayUpdated(theOverlayImg)

    def SetText(self, aText = None):
        self.mText = aText
        self.UpdateOverlay()

    def SetPicture(self, aPicture = None):
        self.mPicture = aPicture
        self.UpdateOverlay()

    def DisplayIcons(self, aCount = None):
        self.mDisplayIconsCount = aCount
        self.UpdateOverlay()

    def GetBlackPicture(self):
        return self.mBlackOverlay
