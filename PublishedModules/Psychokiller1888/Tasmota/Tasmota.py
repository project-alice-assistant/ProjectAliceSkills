# -*- coding: utf-8 -*-

import re

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.device.model.TasmotaConfigs import TasmotaConfigs
from core.dialog.model.DialogSession import DialogSession


class Tasmota(Module):
	"""
	Author: Psychokiller1888
	Description: This module allows you to not only connect tasmota esp devices, but listen to them
	"""

	_CONNECTING = 'projectalice/devices/tasmota/feedback/hello/+'
	_FEEDBACK = 'projectalice/devices/tasmota/feedback/+'

	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_ROOM = Intent('AnswerRoom', isProtected=True)


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._FEEDBACK,
			self._CONNECTING,
			self._INTENT_ANSWER_YES_OR_NO,
			self._INTENT_ANSWER_ROOM
		]

		self._connectingRegex = re.compile(self._CONNECTING.replace('+', '(.*)'))
		self._feedbackRegex = re.compile(self._FEEDBACK.replace('+', '(.*)'))

		self._initializingModule = False
		self._confArray = []
		self._tasmotaConfigs = None

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not intent.startswith('projectalice/devices/tasmota/') and not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		payload = session.payload

		if self._connectingRegex.match(intent):
			identifier = self._connectingRegex.match(intent).group(1)
			if managers.DeviceManager.getDeviceByUID(identifier):
				# This device is known
				self._logger.info('[{}] A device just connected in {}'.format(self.name, siteId))
				managers.DeviceManager.deviceConnecting(uid=identifier)
			else:
				# We did not ask Alice to add a new device
				if not managers.DeviceManager.broadcastFlag.isSet():
					self._logger.warning('[{}] A device is trying to connect to Alice but is unknown'.format(self.name))

		elif self._feedbackRegex.match(intent):
			if 'feedback' in payload:
				if payload['deviceType'] == 'switch':
					if payload['feedback'] > 0:
						managers.ModuleManager.broadcast('onButtonPressed', args=[siteId])
					else:
						managers.ModuleManager.broadcast('onButtonReleased', args=[siteId])
				elif payload['deviceType'] == 'pir':
					if payload['feedback'] > 0:
						managers.ModuleManager.broadcast('onMotionDetected', args=[siteId])
					else:
						managers.ModuleManager.broadcast('onMotionStopped', args=[siteId])

		return True


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, managers.DeviceManager.broadcastRoom)
