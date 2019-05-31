import queue, logging, sys, tty, termios, select, traceback
from RPi import GPIO
from ozPhotoboothEvent import *
from . import ButtonHandler

logger = logging.getLogger(__name__)

class ozPhotoboothInput():
	def __init__(self, aConfig):
		self.mQueue = queue.Queue()
		self.BUTTON_GPIO = aConfig.Get("gpio", "button")

	def Setup(self):
		GPIO.setmode(GPIO.BCM)  # Work with gpio number and not pin number
		GPIO.setup(self.BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		theButtonHandler = ButtonHandler.ButtonHandler(self.BUTTON_GPIO, self.OnButtonTriggered, edge='rising', bouncetime=100)
		theButtonHandler.start()
		
		try:
			GPIO.add_event_detect(self.BUTTON_GPIO, GPIO.BOTH, callback=theButtonHandler)
		except:
			logger.error("Setup Input exeception: " + str(traceback.format_exc()))
			return False

		return True

	def Start(self):
		#self.mOldSettings = termios.tcgetattr(sys.stdin.fileno())
		#tty.setraw(sys.stdin.fileno())
		pass

	def Stop(self):
		if sys.stdin.isatty():
			sys.stdin.close()
		#termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.mOldSettings)
		pass

	def OnButtonTriggered(self, gpio):
		logger.debug("Button Triggered !")
		#Whatever release or press is detected, we send an event. Application will handle multiple events
		self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.PictureButton))

	def Getch(self):
		ch = None

		self.mOldSettings = termios.tcgetattr(sys.stdin.fileno())
		tty.setraw(sys.stdin.fileno())

		if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
			ch = sys.stdin.read(1)
			logger.debug("Getch return: " + str(ch))

		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.mOldSettings)

		return ch

	def GetEvents(self):
		if sys.stdin.isatty():
			input = self.Getch()
			if input == ' ': #SPACE
				self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.PictureButton))
			elif input == '\x1b': #ESCAPE
				self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.ExitButton))

		theEventList = []
		while not self.mQueue.empty():
			theEventList.append(self.mQueue.get())

		return theEventList