import time

from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession
from .models.PhueAPI import Bridge, LinkButtonNotPressed, NoPhueIP, PhueRegistrationError, UnauthorizedUser


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
		self._bridgeConnectTries = 0
		self._stateBackup = dict()

		super().__init__(self._INTENTS)

		self._hueConfigFile = self.getResource(self.name, 'phueAPI.conf')
		if not self._hueConfigFile.exists():
			self.logInfo('No phueAPI.conf file in PhilipsHue module directory')


	def onStart(self) -> dict:
		super().onStart()

		self._bridge = Bridge(ip=self.getConfig('phueBridgeIp'), confFile=self._hueConfigFile)

		if not self.delayed:
			try:
				if self._bridge.connect(autodiscover=not self.getAliceConfig('stayCompletlyOffline')):
					self.logInfo('Connected to Philips Hue bridge')
					return self.supportedIntents

			except UnauthorizedUser:
				try:
					self._bridge.register()
				except LinkButtonNotPressed:
					self.logInfo('User is not authorized')
					self.delayed = True
					raise ModuleStartDelayed(self.name)
				return self.supportedIntents
			except NoPhueIP:
				raise ModuleStartingFailed(moduleName=self.name, error='Bridge IP not set and stay completly offline set to True, cannot auto discover Philips Hue bridge')
		else:
			if not self.ThreadManager.isThreadAlive('PHUERegister'):
				self.ThreadManager.newThread(name='PHUERegister', target=self._registerOnBridge)


	def _registerOnBridge(self):
		try:
			self._bridge.register()
			self._bridgeConnectTries = 0

			self.ThreadManager.doLater(
				interval=3,
				func=self.say,
				args=[self.randomTalk('pressBridgeButtonConfirmation')]
			)
		except LinkButtonNotPressed:
			if self._bridgeConnectTries < 3:
				self.say(text=self.randomTalk('pressBridgeButton'))
				self._bridgeConnectTries += 1
				self.logWarning('Bridge not registered, please press the bridge button, retry in 20 seconds')
				time.sleep(20)
				self._registerOnBridge()
			else:
				self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('pressBridgeButtonTimeout')])
				raise ModuleStartingFailed(moduleName=self.name, error=f"Couldn't reach bridge")
		except PhueRegistrationError as e:
			raise ModuleStartingFailed(moduleName=self.name, error=f'Error connecting to bridge: {e}')


	def onBooted(self):
		super().onBooted()
		if not self.delayed:
			self.onFullHour()


	def onSleep(self):
		self._bridge.group(0).off()


	def onFullHour(self):
		partOfTheDay = self.Commons.partOfTheDay()
		if partOfTheDay not in self._bridge.scenesByName:
			return

		for group in self._bridge.groups.values():
			if group.isOn:
				group.scene(sceneName=partOfTheDay)


	def _getRooms(self, session: DialogSession) -> list:
		rooms = [slot.value['value'].lower() for slot in session.slotsAsObjects.get('Room', list())]
		if not rooms:
			rooms = [constants.DEFAULT_SITE_ID.lower()]

		return rooms if self._validateRooms(session, rooms) else list()


	def _validateRooms(self, session: DialogSession, rooms: list) -> bool:
		for room in rooms:
			if room not in self._bridge.groups and room != constants.EVERYWHERE:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='roomUnknown', replace=[room]))
				return False
		return True


	def lightOnIntent(self, session: DialogSession, **_kwargs):
		partOfTheDay = self.Commons.partOfTheDay()

		rooms = self._getRooms(session)
		for room in rooms:
			try:
				if room == constants.EVERYWHERE:
					self._bridge.group(0).scene(sceneName=partOfTheDay)
					break
				elif partOfTheDay in self._bridge.scenesByName or self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[partOfTheDay].name):
					continue

				for light in self._groups[room].lights:
					light.on = True

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightOffIntent(self, session: DialogSession, **_kwargs):
		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.group(0).off()
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
		elif scene not in self._bridge.scenesByName:
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
				group = self._bridge.group(0)
				group.off() if group.isOn else group.off()
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
				self._bridge.group(0).brightness = brightness
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

		else:
			self._bridge.run_scene(group_name='House', scene_name=scene)
			return

		for g in self._groups:
			self._bridge.run_scene(group_name=g.name, scene_name=scene)


	def lightsOff(self, group: int = 0):
		self._bridge.group(group).off()
