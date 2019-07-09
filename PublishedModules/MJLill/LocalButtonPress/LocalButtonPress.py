# -*- coding: utf-8 -*-

import json
import RPi.GPIO as GPIO
import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Localbuttonpress(Module):
    """
    Author: mjlill
    Description: Press an imaginary button on or off
    """

        _INTENT_BUTTON_ON        = Intent('DoButtonOn')
        _INTENT_BUTTON_OFF       = Intent('DoButtonOff')
        _LIGHT_PIN               = 4

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
                        self._INTENT_BUTTON_ON,
                        self._INTENT_BUTTON_OFF
		]

		super(Localbuttonpress, self).__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId

                if intent == self._INTENT_BUTTON_ON:

                        GPIO.output(_LIGHT_PIN, GPIO.HIGH)

                        managers.MqttServer.endTalk(sessionId, managers.TalkManager.randomTalk(self.name, 'DoButtonOn')client=siteId)


                elif intent == self._INTENT_BUTTON_OFF:

                        GPIO.output(_LIGHT_PIN, GPIO.LOW)

                        managers.MqttServer.endTalk(sessionId, managers.TalkManager.randomTalk(self.name,'DoButtonOff') client=siteId)

		return True
