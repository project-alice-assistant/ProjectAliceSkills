import time

import os
import requests

from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import commons
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
		self._SUPPORTED_INTENTS = [
			self._INTENT_LIGHT_ON,
			self._INTENT_LIGHT_OFF,
			self._INTENT_LIGHT_SCENE,
			self._INTENT_MANAGE_LIGHTS,
			self._INTENT_DIM_LIGHTS,
			self._INTENT_ANSWER_PERCENT,
			self._INTENT_USER_ANSWER
		]

		self._bridge: Bridge = None
		self._groups = dict()
		self._scenes = dict()
		self._bridgeConnectTries = 0
		self._stateBackup = dict()

		self._house = None

		super().__init__(self._SUPPORTED_INTENTS)


	def onStart(self) -> list:
		super().onStart()

		if self.getConfig('phueBridgeIp'):
			if self._connectBridge():
				self.delayed = False
				return self._SUPPORTED_INTENTS
			else:
				self.updateConfig('phueAutodiscoverFallback', True)
				self.updateConfig('phueBridgeIp', '')
		elif self.getConfig('phueAutodiscoverFallback'):
			try:
				request = requests.get('https://www.meethue.com/api/nupnp')
				response = request.json()
				firstBridge = response[0]
				self.logInfo(f"Autodiscover found bridge at {firstBridge['internalipaddress']}, saving ip to config.json")
				self.updateConfig('phueAutodiscoverFallback', False)
				self.updateConfig('phueBridgeIp', firstBridge['internalipaddress'])
				if not self._connectBridge():
					raise ModuleStartingFailed(moduleName=self.name, error='Cannot connect to bridge')
				return self._SUPPORTED_INTENTS
			except IndexError:
				self.logInfo('No bridge found')

		raise ModuleStartingFailed(moduleName=self.name, error='Cannot connect to bridge')


	def _connectBridge(self) -> bool:
		if self._bridgeConnectTries < 3:
			try:
				hueConfigFile = self.getResource(self.name, 'philipsHueConf.conf')
				hueConfigFileExists = os.path.isfile(hueConfigFile)

				if not hueConfigFileExists:
					self.logInfo('No philipsHueConf.conf file in PhilipsHue module directory')

				self._bridge = Bridge(ip=self.ConfigManager.getModuleConfigByName(self.name, 'phueBridgeIp'), config_file_path=hueConfigFile)

				if not self._bridge:
					raise PhueException

				self._bridge.connect()
				if not self._bridge.registered:
					raise PhueRegistrationException

				elif not hueConfigFileExists:
					self.ThreadManager.doLater(
						interval=3,
						func=self.say,
						args=[self.randomTalk('pressBridgeButtonConfirmation')]
					)

			except PhueRegistrationException:
				if self.delayed:
					self.say(text=self.randomTalk('pressBridgeButton'))
					self._bridgeConnectTries += 1
					self.logWarning("-Bridge not registered, please press the bridge button, retry in 20 seconds")
					time.sleep(20)
					return self._connectBridge()
				else:
					self.delayed = True
					raise ModuleStartDelayed(self.name)
			except PhueException as e:
				self.logError(f'Bridge error: {e}')
				return False
		else:
			self.logError("Couldn't reach bridge")
			self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('pressBridgeButtonTimeout')])
			return False

		self._bridgeConnectTries = 0

		for group in self._bridge.groups:
			if 'group for' in group.name.lower():
				continue
			if group.name.lower() == 'house':
				self._house = group
			else:
				self._groups[group.name.lower()] = group

		for scene in self._bridge.scenes:
			self._scenes[scene.name.lower()] = scene

		if self._house is None:
			self.logWarning('Coulnd\'t find any group named "House". Creating one')
			self._bridge.create_group(name='House', lights=self._bridge.get_light().keys(), )

		return True


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
		partOfTheDay = commons.partOfTheDay().lower()
		if partOfTheDay not in self._scenes:
			return

		for group in self._groups.values():
			if group.on:
				self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		siteId = session.siteId
		slots = session.slotsAsObjects
		sessionId = session.sessionId
		customData = session.customData

		if self._bridge is None or not self._bridge.registered:
			self.endDialog(
				sessionId=sessionId,
				text=self.randomTalk('lightBridgeFailure')
			)
			return True

		previousIntent = session.previousIntent

		place = siteId

		room = ''
		if 'Room' in slots:
			for slot in slots['Room']:
				room = slot.value['value'].lower()
				if room not in self._groups.keys() and room != 'everywhere':
					self.endDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='roomUnknown', replace=[room])
					)
					return True

		if 'Scene' in slots:
			for slot in slots['Scene']:
				scene = slot.value['value'].lower()
				if scene not in self._scenes.keys():
					self.endDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='sceneUnknown', replace=[scene])
					)
					return True

		if intent == self._INTENT_LIGHT_ON:
			partOfTheDay = commons.partOfTheDay().lower()
			if 'Room' in slots:
				for slot in slots['Room']:
					room = slot.value['value'].lower()
					if room == 'everywhere':
						self._bridge.set_group(0, 'on', True)
						break

					elif (partOfTheDay not in self._scenes or
						not self._bridge.run_scene(
							group_name=self._groups[room].name,
							scene_name=self._scenes[partOfTheDay].name)):
						for light in self._groups[room].lights:
							light.on = True
			elif place.lower() in self._groups.keys():
				if (partOfTheDay not in self._scenes or
						not self._bridge.run_scene(
							group_name=self._groups[place.lower()].name,
							scene_name=self._scenes[partOfTheDay].name)):
					for light in self._groups[place.lower()].lights:
						light.on = True
			else:
				self.endDialog(sessionId, text=self.randomTalk(text='roomUnknown', replace=[siteId]))
				return True


		elif intent == self._INTENT_LIGHT_OFF:
			if 'Room' in slots:
				for slot in slots['Room']:
					room = slot.value['value'].lower()
					if room == 'everywhere':
						self._bridge.set_group(0, 'on', False)
						break
					else:
						for light in self._groups[room].lights:
							light.on = False
			else:
				if place.lower() in self._groups.keys():
					for light in self._groups[place.lower()].lights:
						light.on = False
				else:
					self.endDialog(sessionId, text=self.randomTalk(text='roomUnknown', replace=[siteId]))
					return True

		elif intent == self._INTENT_LIGHT_SCENE or (previousIntent == self._INTENT_LIGHT_SCENE and intent == self._INTENT_USER_ANSWER):
			if 'Scene' not in slots and 'Scene' not in customData:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('whatScenery'),
					intentFilter=[self._INTENT_USER_ANSWER],
					previousIntent=self._INTENT_LIGHT_SCENE,
					customData={
						'module': self.name,
						'room'  : room
					}
				)
				return True
			else:
				if 'scene' in customData:
					scene = customData['scene']

				elif len(slots['Scene']) > 1:
					self.endDialog(sessionId, text=self.randomTalk('cantSpecifyMoreThanOneScene'))
					return True
				else:
					scene = slots['Scene'][0].value['value'].lower()

				if 'Room' in slots:
					for slot in slots['Room']:
						room = slot.value['value'].lower()
						if not self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[scene].name):
							self.endDialog(sessionId, text=self.randomTalk('sceneNotInThisRoom'))
							return True
				elif not room and 'room' in customData:
					place = customData['room']

				if place.lower() in self._groups.keys():
					if not self._bridge.run_scene(group_name=self._groups[place].name, scene_name=self._scenes[scene].name):
						self.endDialog(sessionId, text=self.randomTalk('sceneNotInThisRoom'))
						return True
				else:
					self.endDialog(sessionId, text=self.randomTalk(text='roomUnknown', replace=[place]))
					return True


		elif intent == self._INTENT_MANAGE_LIGHTS:
			partOfTheDay = commons.partOfTheDay().lower()
			if 'Room' not in slots:
				room = place

				if room not in self._groups.keys():
					self.endDialog(sessionId, text=self.randomTalk(text='roomUnknown', replace=[room]))
					return True

				group = self._groups[room]
				if group.on:
					group.on = False
				elif (partOfTheDay not in self._scenes or
					not self._bridge.run_scene(
						group_name=group.name,
						scene_name=self._scenes[partOfTheDay].name)):
					for light in group.lights:
						light.on = True

			else:
				for slot in slots['Room']:
					room = slot.value['value'].lower()
					if room == 'everywhere':
						self._bridge.set_group(0, 'on', not self._bridge.get_group(0, 'on'))
						break
					else:
						group = self._groups[room]
						if group.on:
							group.on = False
						elif (partOfTheDay not in self._scenes or
							not self._bridge.run_scene(
								group_name=group.name,
								scene_name=self._scenes[partOfTheDay].name)):
							for light in group.lights:
								light.on = True

		elif intent == self._INTENT_DIM_LIGHTS or previousIntent == self._INTENT_DIM_LIGHTS:
			if 'Percent' not in slots:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('whatPercentage'),
					intentFilter=[self._INTENT_ANSWER_PERCENT],
					previousIntent=self._INTENT_DIM_LIGHTS,
					customData={
						'module': self.name
					}
				)
				return True
			else:
				percentage = int(slots['Percent'][0].rawValue.replace('%', ''))
				if percentage < 0:
					percentage = 0
				elif percentage > 100:
					percentage = 100

				brightness = int(round(254 / 100 * percentage))

				if 'Room' not in slots:
					room = siteId.lower()
					if room == 'default':
						room = self.ConfigManager.getAliceConfigByName('room')

					if room not in self._groups.keys():
						self.endDialog(sessionId, text=self.randomTalk(text='roomUnknown', replace=[room]))
						return True

					for light in self._groups[room].lights:
						light.brightness = brightness
				else:
					for slot in slots['Room']:
						room = slot.value['value'].lower()
						if room == 'everywhere':
							self._bridge.set_group(0, 'brightness', brightness)
							break
						else:
							for light in self._groups[room].lights:
								light.brightness = brightness

		self.endDialog(sessionId, text=self.randomTalk('confirm'))
		return True


	def runScene(self, scene, group=None):
		if group is None:
			if self._house is not None:
				self._bridge.run_scene(group_name='House', scene_name=scene)
			else:
				for g in self._groups:
					self._bridge.run_scene(group_name=g.name, scene_name=scene)
		else:
			if type(group) is str:
				name = group
			else:
				name = group.name
			self._bridge.run_scene(group_name=name, scene_name=scene)


	def lightsOff(self, group=0):
		if group == 0:
			self._bridge.set_group(group, 'on', False)
		else:
			for light in self._groups[group].lights:
				light.on = False
