import RPi.GPIO as GPIO

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class LocalButtonPress(Module):
	"""
	Author: mjlill
	Description: Press an imaginary button on or off
	"""

	_INTENT_BUTTON_ON = Intent('DoButtonOn')
	_INTENT_BUTTON_OFF = Intent('DoButtonOff')


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_BUTTON_ON,
			self._INTENT_BUTTON_OFF
		]

		super().__init__(self._SUPPORTED_INTENTS)

		self._gpioPin = self.getConfig('gpioPin')

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self._gpioPin, GPIO.OUT)
		GPIO.output(self._gpioPin, GPIO.LOW)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_BUTTON_ON:
			GPIO.output(self._gpioPin, GPIO.HIGH)
			self.endDialog(session.sessionId, SuperManager.getInstance().talkManager.randomTalk('DoButtonOn'))

		elif intent == self._INTENT_BUTTON_OFF:
			GPIO.output(self._gpioPin, GPIO.LOW)
			self.endDialog(session.sessionId, SuperManager.getInstance().talkManager.randomTalk('DoButtonOff'))

		return True
