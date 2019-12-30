from core.base.model.AliceSkill import AliceSkill
from core.device.model.TasmotaConfigs import TasmotaConfigs
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class Tasmota(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: This skill allows you to not only connect tasmota esp devices, but listen to them
	"""

	def __init__(self):
		self._initializingSkill = False
		self._confArray = []
		self._tasmotaConfigs = None

		super().__init__()


	@MqttHandler('projectalice/devices/tasmota/feedback/hello/+')
	def connectingHandler(self, session: DialogSession):
		identifier = session.intentName.split('/')[-1]
		if self.DeviceManager.getDeviceByUID(identifier):
			# This device is known
			self.logInfo(f'A device just connected in {session.siteId}')
			self.DeviceManager.deviceConnecting(uid=identifier)
		else:
			# We did not ask Alice to add a new device
			if not self.DeviceManager.broadcastFlag.isSet():
				self.logWarning('A device is trying to connect to Alice but is unknown')


	@MqttHandler('projectalice/devices/tasmota/feedback/+')
	def feedbackHandler(self, session: DialogSession):
		siteId = session.siteId
		payload = session.payload

		feedback = payload.get('feedback')
		if not feedback:
			return
		
		deviceType = payload['deviceType']
		
		if deviceType == 'switch':
			if feedback > 0:
				self.SkillManager.skillBroadcast('buttonPressed', siteId=siteId)
			else:
				self.SkillManager.skillBroadcast('buttonReleased', siteId=siteId)
		elif deviceType == 'pir':
			if feedback > 0:
				self.SkillManager.skillBroadcast('motionDetected', siteId=siteId)
			else:
				self.SkillManager.skillBroadcast('motionStopped', siteId=siteId)


	def _initConf(self, identifier: str, deviceBrand: str, deviceType: str):
		self._tasmotaConfigs = TasmotaConfigs(deviceType, identifier)
		self._confArray = self._tasmotaConfigs.getConfigs(deviceBrand, self.DeviceManager.broadcastRoom)
