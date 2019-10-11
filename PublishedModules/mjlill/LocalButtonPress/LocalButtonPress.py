import RPi.GPIO as GPIO

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
		self._INTENTS = {
			self._INTENT_BUTTON_ON: self.buttonOnIntent,
			self._INTENT_BUTTON_OFF: self.buttonOffIntent
		}

		super().__init__(self._INTENTS)

		self._gpioPin = self.getConfig('gpioPin')

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self._gpioPin, GPIO.OUT)
		GPIO.output(self._gpioPin, GPIO.LOW)


	def buttonOnIntent(self, intent: str, session: DialogSession) -> bool:
		GPIO.output(self._gpioPin, GPIO.HIGH)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoButtonOn'))
		return True


	def buttonOffIntent(self, intent: str, session: DialogSession) -> bool:
		GPIO.output(self._gpioPin, GPIO.LOW)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoButtonOff'))
		return True
