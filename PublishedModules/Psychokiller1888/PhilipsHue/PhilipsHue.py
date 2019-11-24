import time

import requests

from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession
from .libraries.phue import Bridge, PhueException, PhueRegistrationException


class PhilipsHue(Module):

	_INTENT_LIGHT_ON = Intent('PowerOnLights')
	_INTENT_LIGHT_OFF = Intent('PowerOffLights')
	_INTENT_LIGHT_SCENE = Intent('SetLightsScene')
	_INTENT_MANAGE_LIGHTS = Intent('ManageLights')
	_INTENT_DIM_LIGHTS = Intent('DimLights')
	_INTENT_ANSWER_PERCENT = Intent('AnswerPercent', isProtected=True)
	_INTENT_USER_ANSWER = Intent('UserRandomAnswer', isProtected=True)


	def __init__(self):
		self._INTENTS = [
			(self._INTENT_LIGHT_ON, self.lightOnIntent),
			(self._INTENT_LIGHT_OFF, self.lightOffIntent),
			(self._INTENT_LIGHT_SCENE, self.lightSceneIntent),
			(self._INTENT_MANAGE_LIGHTS, self.manageLightsIntent),
			(self._INTENT_DIM_LIGHTS, self.dimLightsIntent),
			self._INTENT_ANSWER_PERCENT,
			self._INTENT_USER_ANSWER
		]

		self._INTENT_ANSWER_PERCENT.dialogMapping = {
			'whatPercentage': self.dimLightsIntent
		}

		self._INTENT_USER_ANSWER.dialogMapping = {
			'whatScenery': self.lightSceneIntent
		}

		# noinspection PyTypeChecker
		self._bridge: Bridge = None
		self._groups = dict()
		self._scenes = dict()
		self._bridgeConnectTries = 0
		self._stateBackup = dict()

		self._house = None

		super().__init__(self._INTENTS)

		self._hueConfigFile = self.getResource(self.name, 'philipsHueConf.conf')
		if not self._hueConfigFile.exists():
			self.logInfo('No philipsHueConf.conf file in PhilipsHue module directory')


	def onStart(self) -> dict:
		super().onStart()

		self._bridge = Bridge(ip=self.getConfig('phueBridgeIp'), config_file_path=self._hueConfigFile)

		if not self.delayed:
			if self.getConfig('phueBridgeIp'):
				if not self._isPHUEBridge(self.getConfig('phueBridgeIp')):
					self.logWarning('Configured Philips Hue bridge IP is not a bridge')
					self.updateConfig('phueBridgeIp', '')
					self.delayed = True
					raise ModuleStartDelayed(self.name)

				if not self._bridge.connect():
					self.logWarning("Couldn't connect to bridge")
					self.updateConfig('phueBridgeIp', '')
					self.delayed = True
					raise ModuleStartDelayed(self.name)

				self._setBridgeDefaults()
				return self.supportedIntents
			else:
				self.logInfo(f'Philips Hue bridge IP not set')
				self.delayed = True
				raise ModuleStartDelayed(self.name)
		else:
			if self.getAliceConfig('stayCompletlyOffline'):
				raise ModuleStartingFailed(moduleName=self.name, error='Bridge IP not set and stay completly offline set to True, cannot auto discover Philips Hue bridge')
			elif not self.InternetManager.online:
				raise ModuleStartingFailed(moduleName=self.name, error='Bridge IP not set and currently offline, cannot auto discover Philips Hue bridge')
			try:
				request = requests.get('https://www.meethue.com/api/nupnp')
				for ip in request.json():
					if self._isPHUEBridge(ip['internalipaddress']):
						self._bridge.ip = ip['internalipaddress']
						break

				if not self._bridge.ip:
					raise ModuleStartingFailed(moduleName=self.name, error='No compatible bridge found on network')
			except Exception as e:
				raise ModuleStartingFailed(moduleName=self.name, error=f'Something went wrong trying to autodiscover the bridge: {e}')

			self.ThreadManager.newThread(name='PHUERegister', target=self._registerOnBridge)

		return self.supportedIntents


	def _registerOnBridge(self):
		try:
			self._bridge.register_app()
			self._bridgeConnectTries = 0

			if not self.getConfig('phueBridgeIp'):
				self.updateConfig('phueBridgeIp', self._bridge.ip)
				self.ThreadManager.doLater(
					interval=3,
					func=self.say,
					args=[self.randomTalk('pressBridgeButtonConfirmation')]
				)

			self._setBridgeDefaults()
		except PhueRegistrationException:
			if self._bridgeConnectTries < 3:
				self.say(text=self.randomTalk('pressBridgeButton'))
				self._bridgeConnectTries += 1
				self.logWarning('Bridge not registered, please press the bridge button, retry in 20 seconds')
				time.sleep(20)
				self._registerOnBridge()
			else:
				self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('pressBridgeButtonTimeout')])
				raise ModuleStartingFailed(moduleName=self.name, error=f"Couldn't reach bridge")
		except PhueException as e:
			raise ModuleStartingFailed(moduleName=self.name, error=f'Error connecting to bridge: {e}')


	def _setBridgeDefaults(self):
		for group in self._bridge.groups:
			if not group or 'group for' in group.name.lower():
				continue

			if group.name.lower() == 'house':
				self._house = group
			else:
				self._groups[group.name.lower()] = group

		for scene in self._bridge.scenes:
			self._scenes[scene.name.lower()] = scene

		if self._house is None:
			self.logWarning('Coulnd\'t find any group named "House", creating one...')
			self._bridge.create_group(name='House', lights=[self._bridge.get_light()])


	@staticmethod
	def _isPHUEBridge(ip: str) -> bool:
		try:
			resp = requests.get(f'http://{ip}/api/config', timeout=2)
			data = resp.json()

			if 'swversion' in data and 'bridgeid' in data:
				return True

			return False
		except Exception:
			return False


	@property
	def house(self):
		return self._house


	@property
	def groups(self):
		return self._groups


	@property
	def scenes(self):
		return self._scenes


	def onBooted(self):
		super().onBooted()
		if not self.delayed:
			self.onFullHour()


	def onSleep(self):
		self._bridge.set_group(0, 'on', False)


	def onFullHour(self):
		partOfTheDay = self.Commons.partOfTheDay().lower()
		if partOfTheDay not in self._scenes:
			return

		for group in self._groups.values():
			if group.on:
				self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name)


	def _getRooms(self, session: DialogSession) -> list:
		rooms = [slot.value['value'].lower() for slot in session.slotsAsObjects.get('Room', list())]
		if not rooms:
			rooms = [constants.DEFAULT_SITE_ID.lower()]

		return rooms if self._validateRooms(session, rooms) else list()


	def _validateRooms(self, session: DialogSession, rooms: list) -> bool:
		print(self._groups)
		for room in rooms:
			if room not in self._groups and room != constants.EVERYWHERE:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='roomUnknown', replace=[room]))
				return False
		return True


	def lightOnIntent(self, session: DialogSession, **_kwargs):
		partOfTheDay = self.Commons.partOfTheDay().lower()

		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.set_group(0, 'on', True)
				break
			elif partOfTheDay in self._scenes or self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[partOfTheDay].name):
				continue

			for light in self._groups[room].lights:
				light.on = True

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightOffIntent(self, session: DialogSession, **_kwargs):
		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.set_group(0, 'on', False)
				break

			for light in self._groups[room].lights:
				light.on = False

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightSceneIntent(self, session: DialogSession, **_kwargs):
		sessionId = session.sessionId
		customData = session.customData

		if 'scene' in customData:
			scene = customData['scene']
		elif len(session.slotsAsObjects.get('Scene', list())) > 1:
			self.endDialog(sessionId, text=self.randomTalk('cantSpecifyMoreThanOneScene'))
			return
		else:
			scene = session.slotValue('Scene').lower()

		rooms = self._getRooms(session)
		if not scene:
			self.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('whatScenery'),
				intentFilter=[self._INTENT_USER_ANSWER],
				previousIntent=self._INTENT_LIGHT_SCENE,
				customData={
					'module': self.name,
					'room'  : rooms
				}
			)
			return
		elif scene not in self._scenes:
			self.endDialog(sessionId=sessionId, text=self.randomTalk(text='sceneUnknown', replace=[scene]))
			return

		for room in rooms:
			if not self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[scene].name):
				self.endDialog(sessionId, text=self.randomTalk('sceneNotInThisRoom'))
				return

		if rooms:
			self.endDialog(sessionId, text=self.randomTalk('confirm'))


	def manageLightsIntent(self, session: DialogSession, **_kwargs):
		partOfTheDay = self.Commons.partOfTheDay().lower()

		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.set_group(0, 'on', not self._bridge.get_group(0, 'on'))
				break

			group = self._groups[room]
			if group.on:
				group.on = False
				continue
			elif partOfTheDay in self._scenes or self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name):
				continue

			for light in group.lights:
				light.on = True

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def dimLightsIntent(self, session: DialogSession, **_kwargs):
		if 'Percent' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatPercentage'),
				intentFilter=[self._INTENT_ANSWER_PERCENT],
				previousIntent=self._INTENT_DIM_LIGHTS,
				customData={
					'module': self.name
				}
			)
			return

		percentage = self.Commons.clamp(session.slotValue('Percent'), 0, 100)
		brightness = int(round(254 / 100 * percentage))

		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.set_group(0, 'brightness', brightness)
				break

			for light in self._groups[room].lights:
				light.brightness = brightness

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def runScene(self, scene, group=None):
		if group:
			name = group if isinstance(group, str) else group.name
			self._bridge.run_scene(group_name=name, scene_name=scene)
			return
		if self._house:
			self._bridge.run_scene(group_name='House', scene_name=scene)
			return

		for g in self._groups:
			self._bridge.run_scene(group_name=g.name, scene_name=scene)


	def lightsOff(self, group=0):
		if group == 0:
			self._bridge.set_group(group, 'on', False)
		else:
			for light in self._groups[group].lights:
				light.on = False
