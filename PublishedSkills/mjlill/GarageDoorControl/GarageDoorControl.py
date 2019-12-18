import RPi.GPIO as GPIO

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class GarageDoorControl(AliceSkill):
	"""
	Author: mjlill
	Description: Press an imaginary button on or off
	"""

	def __init__(self):
		super().__init__()

		self._gpioPin = self.getConfig('gpioPin')

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self._gpioPin, GPIO.OUT)
		GPIO.output(self._gpioPin, GPIO.LOW)


	@IntentHandler('DoDoorOpen')
	def buttonOnIntent(self, session: DialogSession, **_kwargs):
		GPIO.output(self._gpioPin, GPIO.HIGH)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoDoorOpen'))

	@IntentHandler('DoDoorClose')
	def buttonOffIntent(self, session: DialogSession, **_kwargs):
		GPIO.output(self._gpioPin, GPIO.LOW)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoDoorClose'))



