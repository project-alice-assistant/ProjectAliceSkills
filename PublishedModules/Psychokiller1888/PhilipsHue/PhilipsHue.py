import time

from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession
from .models.PhueAPI import Bridge, LinkButtonNotPressed, NoPhueIP, NoSuchGroup, NoSuchLight, NoSuchScene, NoSuchSceneInGroup, PhueRegistrationError, UnauthorizedUser


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
			if room == constants.EVERYWHERE:
				try:
					self._bridge.group(0).scene(sceneName=partOfTheDay)
					break
				except NoSuchSceneInGroup:
					self._bridge.group(0).on()
			else:
				try:
					self._bridge.group(groupName=room).scene(sceneName=partOfTheDay)
					break
				except NoSuchSceneInGroup:
					self._bridge.group(groupName=room).on()
				except NoSuchGroup:
					self.logWarning(f'Requested group "{room}" does not exist on the Philips Hue bridge')

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightOffIntent(self, session: DialogSession, **_kwargs):
		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.group(0).off()
				break

			try:
				self._bridge.group(groupName=room).off()
			except NoSuchGroup:
				self.logWarning(f'Requested group "{room}" does not exist on the Philips Hue bridge')

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightSceneIntent(self, session: DialogSession, **_kwargs):
		if len(session.slotsAsObjects.get('Scene', list())) > 1:
			self.endDialog(session.sessionId, text=self.randomTalk('cantSpecifyMoreThanOneScene'))
			return
		else:
			scene = session.slotValue('Scene').lower()

		rooms = self._getRooms(session)
		if not scene:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatScenery'),
				intentFilter=[self._INTENT_USER_ANSWER],
				currentDialogState='whatScenery'
			)
			return
		elif scene not in self._bridge.scenesByName:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='sceneUnknown', replace=[scene]))
			return

		done = False
		for room in rooms:
			try:
				self._bridge.group(groupName=room).scene(sceneName=scene)
				done = True
			except NoSuchSceneInGroup:
				self.logInfo(f'Requested scene "{scene}" for group "{room}" does not exist on the Philips Hue bridge')
			except NoSuchGroup:
				self.logWarning(f'Requested group "{room}" does not exist on the Philips Hue bridge')

		if not done:
			self.endDialog(session.sessionId, text=self.randomTalk('sceneNotInThisRoom'))
			return

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def manageLightsIntent(self, session: DialogSession, **_kwargs):
		partOfTheDay = self.Commons.partOfTheDay().lower()

		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				group = self._bridge.group(0)
				group.off() if group.isOn else group.off()
				break

			try:
				group = self._bridge.group(groupName=room)
				if group.isOn:
					group.off()
					continue

				try:
					group.scene(sceneName=partOfTheDay)
				except NoSuchSceneInGroup:
					for lightId in group.lights:
						self._bridge.light(lightId).on() if self._bridge.light(lightId).isOff else self._bridge.light(lightId).off()
			except NoSuchGroup:
				self.logWarning(f'Requested group "{room}" does not exist on the Philips Hue bridge')
			except NoSuchLight:
				pass

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def dimLightsIntent(self, session: DialogSession, **_kwargs):
		if 'Percent' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatPercentage'),
				intentFilter=[self._INTENT_ANSWER_PERCENT],
				currentDialogState='whatPercentage'
			)
			return

		percentage = self.Commons.clamp(session.slotValue('Percent'), 0, 100)
		brightness = int(round(254 / 100 * percentage))

		rooms = self._getRooms(session)
		for room in rooms:
			if room == constants.EVERYWHERE:
				self._bridge.group(0).brightness = brightness
				break

			try:
				for lightId in self._bridge.group(groupName=room).lights:
					self._bridge.light(lightId).brightness = brightness
			except NoSuchGroup:
				self.logWarning(f'Requested group "{room}" does not exist on the Philips Hue bridge')

		if rooms:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def runScene(self, scene: str, group: str = None):
		try:
			if group:
				self._bridge.group(groupName=group).scene(sceneName=scene)
				return
			else:
				self._bridge.group(0).scene(sceneName=scene)
				return
		except NoSuchGroup:
			self.logWarning(f'Requested group "{group}" does not exist on the Philips Hue bridge')
		except NoSuchScene:
			self.logWarning(f'Requested scene "{scene}" does not exist on the Philips Hue bridge')


	def lightsOff(self, group: int = 0):
		self._bridge.group(group).off()
