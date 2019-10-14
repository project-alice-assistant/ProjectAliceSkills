import re

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


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._FEEDBACK,
			self._CONNECTING
		]

		self._connectingRegex = re.compile(self._CONNECTING.replace('+', '(.*)'))
		self._feedbackRegex = re.compile(self._FEEDBACK.replace('+', '(.*)'))

		self._initializingModule = False
		self._confArray = list()
		self._tasmotaConfigs = None

		self._signals = {
			'switch': ['onButtonPressed', 'onButtonReleased'],
			'pir': ['onMotionDetected', 'onMotionStopped'],
		}

		super().__init__(self._SUPPORTED_INTENTS)


	def filterIntent(self, intent: str, session: DialogSession) -> bool:
		if intent.startswith('projectalice/devices/tasmota/'):
			return True
		return False


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, self.DeviceManager.broadcastRoom)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if self._connectingRegex.match(intent):
			self.connectingIntent(intent, session)
		elif self._feedbackRegex.match(intent):
			self.feebackIntent(intent, session)

		return True


	def connectingIntent(self, intent: str, session: DialogSession):
		identifier = self._connectingRegex.match(intent).group(1)
		if self.DeviceManager.getDeviceByUID(identifier):
			# This device is known
			self._logger.info(f'[{self.name}] A device just connected in {siteId}')
			self.DeviceManager.deviceConnecting(uid=identifier)
		# We did not ask Alice to add a new device
		elif not self.DeviceManager.broadcastFlag.isSet():
			self._logger.warning(f'[{self.name}] A device is trying to connect to Alice but is unknown')


	def feebackIntent(self, intent: str, session: DialogSession):
		siteId = session.siteId
		payload = session.payload

		if not 'feedback' in payload:
			return

		if payload['deviceType'] in {'switch', 'pir'}:
			signal = self._signals[payload['deviceType']] [bool(payload['feedback'])]
			self.ModuleManager.broadcast(signal, args=[siteId])
