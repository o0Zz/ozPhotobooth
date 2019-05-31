import queue, logging
import pygame
from ozPhotoboothEvent import *

logger = logging.getLogger(__name__) 

class ozPhotoboothInput:
	def __init__(self, aConfig):
		self.mQueue = queue.Queue()

	def Setup(self):
		return True

	def Start(self):
		pass

	def Stop(self):
		pass

	def GetEvents(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.PictureButton))
				elif event.key == pygame.K_ESCAPE:
					self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.ExitButton))
					
			if event.type == pygame.QUIT:
				self.mQueue.put(ozPhotoboothEvent(ozPhotoboothEvent.ExitButton))

		theEventList = []
		while not self.mQueue.empty():
			theEventList.append(self.mQueue.get())
			
		return theEventList