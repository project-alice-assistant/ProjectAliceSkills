import re

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
		self._confArray = []
		self._tasmotaConfigs = None

		super().__init__(self._SUPPORTED_INTENTS)


	def filterIntent(self, session: DialogSession) -> bool:
		if session.intentName.startswith('projectalice/devices/tasmota/'):
			return True
		return super().filterIntent(session=session)


	def onMessage(self, session: DialogSession):
		siteId = session.siteId
		payload = session.payload
		intent = session.intentName

		if self._connectingRegex.match(intent):
			identifier = self._connectingRegex.match(intent).group(1)
			if self.DeviceManager.getDeviceByUID(identifier):
				# This device is known
				self.logInfo(f'A device just connected in {siteId}')
				self.DeviceManager.deviceConnecting(uid=identifier)
			else:
				# We did not ask Alice to add a new device
				if not self.DeviceManager.broadcastFlag.isSet():
					self.logWarning('A device is trying to connect to Alice but is unknown')

		elif self._feedbackRegex.match(intent):
			if 'feedback' in payload:
				if payload['deviceType'] == 'switch':
					if payload['feedback'] > 0:
						self.ModuleManager.moduleBroadcast('onButtonPressed', args=[siteId])
					else:
						self.ModuleManager.moduleBroadcast('onButtonReleased', args=[siteId])
				elif payload['deviceType'] == 'pir':
					if payload['feedback'] > 0:
						self.ModuleManager.moduleBroadcast('onMotionDetected', args=[siteId])
					else:
						self.ModuleManager.moduleBroadcast('onMotionStopped', args=[siteId])


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, self.DeviceManager.broadcastRoom)
