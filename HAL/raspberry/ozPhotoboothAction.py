import time
from RPi import GPIO

class ozPhotoboothAction:
	def __init__(self, aConfig):		
		self.LED_BUTTON_GPIO = aConfig.Get("gpio", "led_button")
		self.LIGHT_GPIO = aConfig.Get("gpio", "light")
		self.MONITOR_GPIO = aConfig.Get("gpio", "monitor")

	def Setup(self):
		GPIO.setmode(GPIO.BCM)  # Work with gpio number and not pin number

		GPIO.setup(self.LED_BUTTON_GPIO, GPIO.OUT)
		GPIO.output(self.LED_BUTTON_GPIO, GPIO.LOW)

		GPIO.setup(self.LIGHT_GPIO, GPIO.OUT)
		GPIO.output(self.LIGHT_GPIO, GPIO.LOW)

		GPIO.setup(self.MONITOR_GPIO, GPIO.OUT)
		GPIO.output(self.MONITOR_GPIO, GPIO.LOW)

		return True

	def Start(self):
		self.__ToggleMonitorOnOff();

	def Stop(self):
		GPIO.cleanup()

	def __ToggleMonitorOnOff(self):
		GPIO.output(self.MONITOR_GPIO, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(self.MONITOR_GPIO, GPIO.LOW)

	def SetButtonLed(self, afON):
		if afON:
			GPIO.output(self.LED_BUTTON_GPIO, GPIO.HIGH)
		else:
			GPIO.output(self.LED_BUTTON_GPIO, GPIO.LOW)

	def SetLight(self, afON):
		if afON:
			GPIO.output(self.LIGHT_GPIO, GPIO.HIGH)
		else:
			GPIO.output(self.LIGHT_GPIO, GPIO.LOW)
