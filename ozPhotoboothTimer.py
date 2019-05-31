import time, threading, logging

logger = logging.getLogger(__name__) 

class ozPhotoboothTimer(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

		self.mLock = threading.Lock()
		self.mTimerList = []
		self.mCurrentTimerID = 0
	
	@staticmethod
	def _time_now_ms():
		return int(round(time.time() * 1000))
	
	@staticmethod
	def _time_elapsed_ms(aTime):
		return ozPhotoboothTimer._time_now_ms() - aTime 
	
	def Start(self):
		self.mfRunning = True
		self.start()
	
	def Stop(self):
		self.mfRunning = False
		self.join()
		
	def StartTimer(self, aTimeoutMs, anExpireCallback, anExpireCallbackCtx):
		self.mCurrentTimerID = self.mCurrentTimerID + 1
		
		theTimer = {}
		theTimer["id"] 					= self.mCurrentTimerID
		theTimer["expire_callback"] 	= anExpireCallback
		theTimer["expire_callback_ctx"] = anExpireCallbackCtx
		theTimer["start_time_ms"] 		= ozPhotoboothTimer._time_now_ms()
		theTimer["timeout_ms"] 			= aTimeoutMs
		
		logger.debug("New timer expired in " + str(aTimeoutMs) + " ms")
					
					
		with self.mLock:
			self.mTimerList.append(theTimer)
			
		return self.mCurrentTimerID
		
	def StopTimer(self, anID):
		with self.mLock:
			for i in range(0, len(self.mTimerList)):
				if self.mTimerList[i]["id"] == anID:
					self.mTimerList.pop(i)
					break
		
	def run(self):
		while self.mfRunning:
			with self.mLock:
				i = 0
				for theTimer in self.mTimerList:
					theExpiredTimeMs = ozPhotoboothTimer._time_elapsed_ms(self.mTimerList[i]["start_time_ms"])
					
					#logger.debug("expired ?: " + str(theExpiredTimeMs) + " >= " + str(self.mTimerList[i]["timeout_ms"]))
					
					if theExpiredTimeMs >= self.mTimerList[i]["timeout_ms"]:
						theTimer["expire_callback"]( theTimer["expire_callback_ctx"] )
						self.mTimerList.pop(i)
					else:
						i = i + 1
					
					
			time.sleep(0.01) # Sleep 10ms
		
		logger.debug("Timer thread exit !")
			