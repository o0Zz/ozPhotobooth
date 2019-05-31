import RPi.GPIO as GPIO
import threading, logging

logger = logging.getLogger(__name__)

#GPIO.setmode(GPIO.BCM)  # Work with gpio number and not pin number
#GPIO.setup(self.BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#theButtonHandler = ButtonHandler.ButtonHandler(self.BUTTON_GPIO, self.OnButtonTriggered, edge='rising', bouncetime=100)
#theButtonHandler.start()
#try:
#	GPIO.add_event_detect(self.BUTTON_GPIO, GPIO.BOTH, callback=theButtonHandler)
#except:
#	logger.error("Setup Input exeception: " + str(traceback.format_exc()))


class ButtonHandler(threading.Thread):
	def __init__(self, pin, func, edge='both', bouncetime=200):
		super().__init__(daemon=True)
		self.edge = edge
		self.func = func
		self.pin = pin
		self.bouncetime = float(bouncetime)/1000

		self.lastpinval = GPIO.input(self.pin)
		self.lock = threading.Lock()

	def __call__(self, *args):
		if not self.lock.acquire(blocking=False):
			return

		t = threading.Timer(self.bouncetime, self.read, args=args)
		t.start()

	def read(self, *args):
		pinval = GPIO.input(self.pin)
		
		#logger.debug("ButtonRead: pinval=" + str(pinval) + " lastpinval=" + str(self.lastpinval))
		
		if ((pinval == 0 and self.lastpinval == 1) and (self.edge in ['falling', 'both'])) or ((pinval == 1 and self.lastpinval == 0) and (self.edge in ['rising', 'both'])):
			self.func(*args)

		self.lastpinval = pinval
		self.lock.release()