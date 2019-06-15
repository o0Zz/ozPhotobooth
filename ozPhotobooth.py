#!/usr/bin/python3
#
# pip install zipstream
# pip install pygame
# pip install opencv-python
# pip install Pillow

import sys, os, threading, logging, traceback
import ozPhotoboothConfig, ozPhotoboothTimer, ozPhotoboothSound, ozPhotoboothPhotoDisk, ozPhotoboothPhotoPreview, ozPhotoboothSequence, ozPhotoboothEvent
import time
import subprocess
import re
from network import ozDNSManager

from ozPhotoboothHTTPServer import *

if os.name != 'nt' and os.uname()[1] == 'raspberrypi':
	from HAL.raspberry import ozPhotoboothAction, ozPhotoboothInput, ozPhotoboothCamera
else:
	from HAL.generic import ozPhotoboothAction, ozPhotoboothInput, ozPhotoboothCamera

logger = logging.getLogger(__name__)

CONFIGURATION_FILENAME = "./ozPhotobooth.cfg"

# ================================================= 
		
class ozPhotobooth():
	def __init__(self):
		self.mfRunning = True
		self.mCamera = None
		self.mInput = None
		self.mAction = None
		self.mSequencer = None
		self.mHTTPServer = None
		self.mSound = None
		self.mPhotoDisk = None
		self.mDNSManager = None
		
	def Setup(self, aConfigFilename):
		self.mConfig = ozPhotoboothConfig.ozPhotoboothConfig(aConfigFilename)
		if not self.mConfig.isLoaded():
			logger.error("Unable to load configuration !")
			return False

		logger.debug("Loading camera ...")
		self.mCamera = ozPhotoboothCamera.ozPhotoboothCamera(self.mConfig)
		if not self.mCamera.Setup():
			logger.error("Unable to setup camera !")
			return False
		
		self.mCamera.Start()
		self.mCamera.StartPreview()

		logger.debug("Loading sound ...")
		self.mSound = ozPhotoboothSound.ozPhotoboothSound(self.mConfig)
		
		logger.debug("Loading disck ...")
		self.mPhotoDisk = ozPhotoboothPhotoDisk.ozPhotoboothPhotoDisk(self.mConfig)
		
		logger.debug("Loading HTTPServer ...")
		self.mHTTPServer = ozPhotoboothHTTPServer(self.mConfig, self.mPhotoDisk)
		
		logger.debug("Loading input ...")
		
		self.mInput = ozPhotoboothInput.ozPhotoboothInput(self.mConfig)
		if not self.mInput.Setup():
			logger.error("Unable to setup input !")
			return False

		self.mInput.Start()

		logger.debug("Loading Action ...")
		self.mAction = ozPhotoboothAction.ozPhotoboothAction(self.mConfig)
		if not self.mAction.Setup():
			logger.error("Unable to setup Action !")
			return False

		self.mAction.Start()

		logger.debug("Loading DNSServer ...")
		theDNSServerIP = self.mConfig.GetDNSServerIP()
		if len(theDNSServerIP) > 0:
			self.mDNSManager = ozDNSManager.ozDNSManager(theDNSServerIP)
			self.mDNSManager.Start()
			
		return True

	def Quit(self):
		self.mfRunning = False

		logger.info("Photobooth exiting...")

		if self.mSequencer != None and self.mSequencer.IsRunning():
			self.mSequencer.Stop()

		if self.mInput != None:
			self.mInput.Stop()

		if self.mAction != None:
			self.mAction.Stop()

		if self.mHTTPServer != None:
			self.mHTTPServer.Stop()

		if self.mCamera != None:
			self.mCamera.Stop()

		if self.mDNSManager != None:
			self.mDNSManager.Stop()
			
	def Run(self):
		logger.info("Photobooth running...")
			
		while self.mfRunning:
			try:
				
				#Handle events
				for event in self.mInput.GetEvents():
				
					if self.mSequencer == None or self.mSequencer.IsDone():
						self.mSequencer = ozPhotoboothSequence.ozPhotoboothSequence(self.mConfig, self.mCamera, self.mAction, self.mSound, self.mPhotoDisk)

					if event.type == ozPhotoboothEvent.ozPhotoboothEvent.ExitButton:
						self.mfRunning = False
					elif event.type == ozPhotoboothEvent.ozPhotoboothEvent.PictureButton:
						if self.mSequencer != None and not self.mSequencer.IsRunning() and not self.mSequencer.IsDone():
							self.mSequencer.Start()

				#Avoid infinite loop
				time.sleep(0.1)

			except Exception as e:
				logger.error("Photobooth exeception: " + str(traceback.format_exc()))
				self.mfRunning = False
				
# ================================================= 

def CheckIPTables():
	#List all: "sudo iptable -L"
	#List prerouting: "sudo iptables -L -n -t nat"
	#Delete a route: "sudo iptables -t nat -D PREROUTING 1"
	#if os.name != 'nt' and os.uname()[1] == 'raspberrypi':
	#	os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 192.168.4.1:8080")
	#	os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:8080")
	#	os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
	#REDIRECT   tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:80 redir ports 8080

	if os.name != 'nt' and os.uname()[1] == 'raspberrypi':
		process = subprocess.Popen(['iptables -L -n -t nat'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		stdout = process.communicate()[0]

		thefHasRedirect80To8080 = False
		theLines = str(stdout).split("\\n")
		for line in theLines:
			#logger.debug("Parsing iptable line: " + str(line))
			if bool(re.search("REDIRECT.*tcp dpt:80 redir ports 8080", str(line))):
				logger.info("Route from port 80 to 8080 found, nothing to do.")
				thefHasRedirect80To8080 = True
		
		if not thefHasRedirect80To8080:
			logger.info("No route found for forwarding port 80 to port 8080, adding it ...")
			os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
				
# ================================================= 

def AutoMountUSB():
	kUSBKeyPath = ["/dev/sda1", "/dev/sdb1", "/dev/sdc1"]
	if os.name != 'nt' and os.uname()[1] == 'raspberrypi':
		for theDevPath in kUSBKeyPath:
			if os.path.exists(theDevPath):
				logger.info("Trying to mount " + theDevPath + " to /media/pi/usb")
				os.system("sudo umount /media/pi/usb")
				os.system("sudo mkdir -p /media/pi/usb")	
				os.system("sudo mount " + theDevPath + " /media/pi/usb")
				return
			
		logger.error("Unable to mount USB key: " + kUSBKeyPath + " not found !")

# ================================================= 
	
if __name__ == '__main__':

	# logging.basicConfig(filename='ozPhotobooth.log', level=logging.DEBUG, format='%(asctime)s %(module)s: %(levelname)-8s %(message)s')
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
						format='%(asctime)s %(module)32s: %(levelname)-8s %(message)s\r')

	#Working directory is the script directory
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	os.environ["DISPLAY"] = ":0.0"
	
	if os.name != 'nt' and os.uname()[1] == 'raspberrypi':
		if os.geteuid() != 0:
			logger.error("You need to execute this script as root !")
			sys.exit(1)
	
	CheckIPTables()
	AutoMountUSB()
	
	thePhotobooth = ozPhotobooth()

	if thePhotobooth.Setup(CONFIGURATION_FILENAME):
		thePhotobooth.Run()

	thePhotobooth.Quit()

	logger.debug("Program exit !")
