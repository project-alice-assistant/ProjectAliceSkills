# -*- coding: utf-8 -*-

import json
import os
import time

import requests

import core.base.Managers as managers
from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession
from modules.PhilipsHue.libraries.phue import Bridge, PhueException, PhueRegistrationException


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

		self._bridge = None
		self._groups = dict()
		self._scenes = dict()
		self._bridgeConnectTries = 0
		self._stateBackup = {}

		self._house = None

		super().__init__(self._SUPPORTED_INTENTS)


	def onStart(self) -> list:
		if managers.ConfigManager.getModuleConfigByName(self.name, 'phueBridgeIp'):
			if self._connectBridge():
				self.delayed = False
				return super().onStart()
			else:
				managers.ConfigManager.updateModuleConfigurationFile(self.name, 'phueAutodiscoverFallback', True)
				managers.ConfigManager.updateModuleConfigurationFile(self.name, 'phueBridgeIp', '')
		elif managers.ConfigManager.getModuleConfigByName(self.name, 'phueAutodiscoverFallback'):
			try:
				request = requests.get('https://www.meethue.com/api/nupnp')
				response = request.json()
				firstBridge = response[0]
				self._logger.info("- [{}] Autodiscover found bridge at {}, saving ip to config.json".format(self.name, firstBridge['internalipaddress']))
				managers.ConfigManager.updateModuleConfigurationFile(self.name, 'phueAutodiscoverFallback', False)
				managers.ConfigManager.updateModuleConfigurationFile(self.name, 'phueBridgeIp', firstBridge['internalipaddress'])
				return self.onStart()
			except IndexError:
				self._logger.info("- [{}] No bridge found".format(self.name))

		raise ModuleStartingFailed(moduleName=self.name, error='[{}] Cannot connect to bridge'.format(self.name))


	def _connectBridge(self) -> bool:
		if self._bridgeConnectTries < 3:
			try:
				hueConfigFile = self.getResource(self.name, "philipsHueConf.conf")
				hueConfigFileExists = os.path.isfile(hueConfigFile)

				if not hueConfigFileExists:
					self._logger.info('- [{}] No philipsHueConf.conf file in PhilipsHue module directory'.format(self.name))

				self._bridge = Bridge(ip=managers.ConfigManager.getModuleConfigByName(self.name, 'phueBridgeIp'), config_file_path=hueConfigFile)

				if not self._bridge:
					raise PhueException

				self._bridge.connect()
				if not self._bridge.registered:
					raise PhueRegistrationException
				else:
					if not hueConfigFileExists:
						managers.ThreadManager.doLater(interval=3, func=managers.MqttServer.say, args=[managers.TalkManager.randomTalk('pressBridgeButtonConfirmation')])
			except PhueRegistrationException:
				if self.delayed:
					managers.MqttServer.say(text=managers.TalkManager.randomTalk('pressBridgeButton'))
					self._bridgeConnectTries += 1
					self._logger.warning("- [{}] Bridge not registered, please press the bridge button, retry in 20 seconds".format(self.name))
					time.sleep(20)
					return self._connectBridge()
				else:
					self.delayed = True
					raise ModuleStartDelayed(self.name)
			except PhueException as e:
				self._logger.error('- [{}] Bridge error: {}'.format(self.name, e))
				return False
		else:
			self._logger.error("- [{}] Couldn't reach bridge".format(self.name))
			managers.ThreadManager.doLater(interval=3, func=managers.MqttServer.say, args=[managers.TalkManager.randomTalk('pressBridgeButtonTimeout')])
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
			self._logger.warning('- [{}] Coulnd\'t find any group named "House". Creating one'.format(self.name))
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
		for group in self._groups.values():
			if group.on:
				self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slotsAsObjects
		sessionId = session.sessionId
		customData = session.customData

		if self._bridge is None or not self._bridge.registered:
			managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('lightBridgeFailure'), client=siteId)
			return True

		previousIntent = session.previousIntent

		place = siteId if siteId != 'default' else managers.ConfigManager.getAliceConfigByName('room')

		room = ''
		if 'Room' in slots:
			for slot in slots['Room']:
				room = slot.value['value'].lower()
				if room not in self._groups.keys() and room != 'everywhere':
					managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(room), client=siteId)
					return True

		if 'Scene' in slots:
			for slot in slots['Scene']:
				scene = slot.value['value'].lower()
				if scene not in self._scenes.keys():
					managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('sceneUnknown').format(scene), client=siteId)
					return True

		if intent == self._INTENT_LIGHT_ON:
			partOfTheDay = commons.partOfTheDay().lower()
			if 'Room' in slots:
				for slot in slots['Room']:
					room = slot.value['value'].lower()
					if room == 'everywhere':
						self._bridge.set_group(0, 'on', True)
						break
					else:
						if partOfTheDay not in self._scenes:
							for light in self._groups[room].lights:
								light.on = True
						else:
							if not self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[partOfTheDay].name):
								for light in self._groups[room].lights:
									light.on = True
			else:
				if place.lower() in self._groups.keys():
					if partOfTheDay not in self._scenes:
						for light in self._groups[place.lower()].lights:
							light.on = True
					else:
						if not self._bridge.run_scene(group_name=self._groups[place.lower()].name, scene_name=self._scenes[partOfTheDay].name):
							for light in self._groups[place.lower()].lights:
								light.on = True
				else:
					managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(siteId), client=siteId)
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
					managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(siteId), client=siteId)
					return True

		elif intent == self._INTENT_LIGHT_SCENE or (previousIntent == self._INTENT_LIGHT_SCENE and intent == self._INTENT_USER_ANSWER):
			if 'Scene' not in slots and 'Scene' not in customData:
				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=managers.TalkManager.randomTalk('whatScenery'),
					intentFilter=[self._INTENT_USER_ANSWER],
					previousIntent=self._INTENT_LIGHT_SCENE,
					customData=json.dumps({
						'module': self.name,
						'room'  : room
					})
				)
				return True
			else:
				if 'scene' in customData:
					scene = customData['scene']
				else:
					if len(slots['Scene']) > 1:
						managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('cantSpecifyMoreThanOneScene'), client=siteId)
						return True
					else:
						scene = slots['Scene'][0].value['value'].lower()

				if 'Room' in slots:
					for slot in slots['Room']:
						room = slot.value['value'].lower()
						if not self._bridge.run_scene(group_name=self._groups[room].name, scene_name=self._scenes[scene].name):
							managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('sceneNotInThisRoom'), client=siteId)
							return True
				else:
					if not room and 'room' in customData:
						place = customData['room']

					if place.lower() in self._groups.keys():
						if not self._bridge.run_scene(group_name=self._groups[place].name, scene_name=self._scenes[scene].name):
							managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('sceneNotInThisRoom'), client=siteId)
							return True
					else:
						managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(place), client=siteId)
						return True

		elif intent == self._INTENT_MANAGE_LIGHTS:
			partOfTheDay = commons.partOfTheDay().lower()
			if 'Room' not in slots:
				room = place

				if room not in self._groups.keys():
					managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(room), client=siteId)
					return True

				group = self._groups[room]
				if group.on:
					group.on = False
				else:
					if partOfTheDay not in self._scenes:
						for light in group.lights:
							light.on = True
					else:
						if not self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name):
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
						else:
							if partOfTheDay not in self._scenes:
								for light in group.lights:
									light.on = True
							else:
								if not self._bridge.run_scene(group_name=group.name, scene_name=self._scenes[partOfTheDay].name):
									for light in group.lights:
										light.on = True

		elif intent == self._INTENT_DIM_LIGHTS or previousIntent == self._INTENT_DIM_LIGHTS:
			if 'Percent' not in slots:
				managers.MqttServer.ask(
					sessionId=sessionId,
					text=managers.TalkManager.randomTalk('whatPercentage'),
					intentFilter=[self._INTENT_ANSWER_PERCENT],
					previousIntent=self._INTENT_DIM_LIGHTS,
					customData=json.dumps({
						'module': self.name
					})
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
						room = managers.ConfigManager.getAliceConfigByName('room')

					if room not in self._groups.keys():
						managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('roomUnknown').format(room), client=siteId)
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

		managers.MqttServer.endTalk(sessionId, text=managers.TalkManager.randomTalk('confirm'))
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
