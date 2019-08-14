# -*- coding: utf-8 -*-

import getpass
import json
import subprocess
import time
from zipfile import ZipFile

import core.base.Managers as managers
from core.ProjectAliceExceptions import ConfigurationUpdateFailed, LanguageManagerLangNotSupported, ModuleStartDelayed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession
from core.voice.WakewordManager import WakewordManagerState


class AliceCore(Module):
	_DEVING_CMD = 'projectAlice/deving'

	_INTENT_MODULE_GREETING = 'projectAlice/devices/greeting'
	_INTENT_GLOBAL_STOP = Intent('GlobalStop')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_ROOM = Intent('AnswerRoom', isProtected=True)
	_INTENT_SWITCH_LANGUAGE = Intent('SwitchLanguage')
	_INTENT_UPDATE_ALICE = Intent('DoAliceUpdate', isProtected=True)
	_INTENT_REBOOT = Intent('RebootSystem')
	_INTENT_INVADE_SONOS = Intent('InvadeSonos')
	_INTENT_RETREAT = Intent('RetreatSonos')
	_INTENT_STOP_LISTEN = Intent('StopListening')
	_INTENT_ADD_DEVICE = Intent('AddComponent')
	_INTENT_ANSWER_HARDWARE_TYPE = Intent('AnswerHardwareType', isProtected=True)
	_INTENT_ANSWER_ESP_TYPE = Intent('AnswerEspType', isProtected=True)
	_INTENT_ANSWER_NAME = Intent('AnswerName', isProtected=True)
	_INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)
	_INTENT_ANSWER_WAKEWORD_CUTTING = Intent('AnswerWakewordCutting', isProtected=True)
	_INTENT_DUMMY_ADD_USER = Intent('DummyUser', isProtected=True)
	_INTENT_DUMMY_ADD_WAKEWORD = Intent('DummyWakeword', isProtected=True),
	_INTENT_DUMMY_WAKEWORD_INSTRUCTION = Intent('DummyInstruction', isProtected=True)
	_INTENT_DUMMY_WAKEWORD_OK = Intent('DummyWakewordOk', isProtected=True)
	_INTENT_WAKEWORD = Intent('CallWakeword', isProtected=True)


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_GLOBAL_STOP,
			self._INTENT_MODULE_GREETING,
			self._INTENT_ANSWER_YES_OR_NO,
			self._INTENT_ANSWER_ROOM,
			self._INTENT_SWITCH_LANGUAGE,
			self._INTENT_UPDATE_ALICE,
			self._INTENT_REBOOT,
			self._INTENT_INVADE_SONOS,
			self._INTENT_RETREAT,
			self._INTENT_STOP_LISTEN,
			self._DEVING_CMD,
			self._INTENT_ADD_DEVICE,
			self._INTENT_ANSWER_HARDWARE_TYPE,
			self._INTENT_ANSWER_ESP_TYPE,
			self._INTENT_ANSWER_NAME,
			self._INTENT_SPELL_WORD,
			self._INTENT_DUMMY_ADD_USER,
			self._INTENT_DUMMY_ADD_WAKEWORD,
			self._INTENT_DUMMY_WAKEWORD_INSTRUCTION,
			self._INTENT_ANSWER_WAKEWORD_CUTTING,
			self._INTENT_DUMMY_WAKEWORD_OK,
			self._INTENT_WAKEWORD
		]

		self._threads = dict()
		super().__init__(self._SUPPORTED_INTENTS)


	def onStart(self):
		self.changeFeedbackSound(inDialog=False)

		if len(managers.UserManager.users) <= 0:
			if not self.delayed:
				self._logger.warning('[{}] No user found in database'.format(self.name))
				raise ModuleStartDelayed(self.name)
			else:
				self._addFirstUser()
		else:
			return super().onStart()


	def _addFirstUser(self):
		managers.MqttServer.ask(
			text=self.randomTalk('addAdminUser'),
			intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
			previousIntent=self._INTENT_DUMMY_ADD_USER,
			canBeEnqueued=False
		)


	def onUserCancel(self, session: DialogSession):
		if self.delayed:
			managers.MqttServer.say(text=self.randomTalk('noStartWithoutAdmin'), client=session.siteId)
			self.delayed = False

			def stop():
				subprocess.run(['sudo', 'systemctl', 'stop', 'ProjectAlice'])

			managers.ThreadManager.doLater(interval=10, func=stop)


	def onSessionTimeout(self, session: DialogSession):
		if self.delayed:
			self._addFirstUser()


	def onSessionError(self, session: DialogSession):
		if self.delayed:
			self._addFirstUser()


	def onSessionStarted(self, session: DialogSession):
		self.changeFeedbackSound(inDialog=True)


	def onSessionEnded(self, session: DialogSession):
		if not managers.ThreadManager.getLock('AddingWakeword').isSet():
			self.changeFeedbackSound(inDialog=False)

			if self.delayed:
				self._addFirstUser()


	def onSleep(self):
		managers.MqttServer.toggleFeedbackSounds('off')


	def onWakeup(self):
		managers.MqttServer.toggleFeedbackSounds('on')


	def onBooted(self):
		if not super().onBooted():
			return

		onReboot = managers.ConfigManager.getAliceConfigByName('onReboot')
		if onReboot:
			if onReboot == 'greet':
				managers.ThreadManager.doLater(interval=3, func=managers.MqttServer.say, args=[self.randomTalk('confirmRebooted'), 'all'])
			elif onReboot == 'greetAndRebootModules':
				managers.ThreadManager.doLater(interval=3, func=managers.MqttServer.say, args=[self.randomTalk('confirmRebootingModules'), 'all'])
			else:
				self._logger.warning('[{}] onReboot config has an unknown value'.format(self.name))

			managers.ConfigManager.updateAliceConfiguration('onReboot', '')
		else:
			managers.ThreadManager.doLater(interval=3, func=managers.MqttServer.playSound, args=[self.getResource(self.name, 'sounds/boot.wav'), 'boot-session-id', True, 'all'])


	def onGoingBed(self):
		managers.UserManager.goingBed()


	def onLeavingHome(self):
		managers.UserManager.leftHome()


	def onReturningHome(self):
		managers.UserManager.home()


	def onSayFinished(self, session: DialogSession):
		if managers.ThreadManager.getLock('AddingWakeword').isSet() and managers.WakewordManager.state == WakewordManagerState.IDLE:
			managers.WakewordManager.addASample()


	def onSnipsAssistantDownloaded(self, *args):
		try:
			with ZipFile('/tmp/assistant.zip') as zipfile:
				zipfile.extractall('/tmp')

			subprocess.run(['sudo', 'rm', '-rf', commons.rootDir() + '/trained/assistants/assistant_{}'.format(managers.LanguageManager.activeLanguage)])
			subprocess.run(['sudo', 'cp', '-R', '/tmp/assistant', commons.rootDir() + '/trained/assistants/assistant_{}'.format(managers.LanguageManager.activeLanguage)])
			subprocess.run(['sudo', 'chown', '-R', getpass.getuser(), commons.rootDir() + '/trained/assistants/assistant_{}'.format(managers.LanguageManager.activeLanguage)])

			subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/trained/assistants/assistant_{}'.format(managers.LanguageManager.activeLanguage), commons.rootDir() + '/assistant'])
			subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/system/sounds/{}/start_of_input.wav'.format(managers.LanguageManager.activeLanguage), commons.rootDir() + '/assistant/custom_dialogue/sound/start_of_input.wav'])
			subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/system/sounds/{}/end_of_input.wav'.format(managers.LanguageManager.activeLanguage), commons.rootDir() + '/assistant/custom_dialogue/sound/end_of_input.wav'])
			subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/system/sounds/{}/error.wav'.format(managers.LanguageManager.activeLanguage), commons.rootDir() + '/assistant/custom_dialogue/sound/error.wav'])

			managers.SnipsServicesManager.runCmd('restart')

			managers.MqttServer.say(text=self.randomTalk('confirmBundleUpdate'))
		except:
			managers.MqttServer.say(text=self.randomTalk('bundleUpdateFailed'))


	def onSnipsAssistantDownloadFailed(self, *args):
		managers.MqttServer.say(text=self.randomTalk('bundleUpdateFailed'))


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if intent == self._INTENT_GLOBAL_STOP:
			managers.MqttServer.endTalk(sessionId=session.sessionId, text=self.randomTalk('confirmGlobalStop'), client=session.siteId)
			return True
		
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slots
		slotsObj = session.slotsAsObjects
		sessionId = session.sessionId
		customData = session.customData
		payload = session.payload

		if intent == self._INTENT_ADD_DEVICE or session.previousIntent == self._INTENT_ADD_DEVICE:
			if managers.DeviceManager.isBusy():
				managers.MqttServer.endTalk(sessionId=sessionId,
											text=self.randomTalk('busy'),
											client=siteId)
				return True

			if 'Hardware' not in slots:
				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('whatHardware'),
					intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
					previousIntent=self._INTENT_ADD_DEVICE
				)
				return True

			elif slotsObj['Hardware'][0].value['value'] == 'esp' and 'EspType' not in slots:
				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('whatESP'),
					intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
					previousIntent=self._INTENT_ADD_DEVICE
				)
				return True

			elif 'Room' not in slots:
				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('whichRoom'),
					intentFilter=[self._INTENT_ANSWER_ROOM],
					previousIntent=self._INTENT_ADD_DEVICE
				)
				return True

			hardware = slotsObj['Hardware'][0].value['value']
			if hardware == 'esp':
				if not managers.ModuleManager.isModuleActive('Tasmota'):
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('requireTasmotaModule'))
					return True

				if managers.DeviceManager.isBusy():
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('busy'))
					return True

				if not managers.DeviceManager.startTasmotaFlashingProcess(commons.cleanRoomNameToSiteId(slots['Room']), slotsObj['EspType'][0].value['value'], session):
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('espFailed'))

			elif hardware == 'satellite':
				if managers.DeviceManager.startBroadcastingForNewDevice(commons.cleanRoomNameToSiteId(slots['Room']), siteId):
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('confirmDeviceAddingMode'))
				else:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('busy'))
			else:
				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('unknownHardware'),
					intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE],
					previousIntent=self._INTENT_ADD_DEVICE
				)
				return True

		elif intent == self._INTENT_MODULE_GREETING:
			if 'uid' not in payload or 'siteId' not in payload:
				self._logger.warning('A device tried to connect but is missing informations in the payload, refused')
				managers.MqttServer.publish(topic='projectAlice/devices/connectionRefused', payload=json.dumps({'siteId': payload['siteId']}))
				return True

			device = managers.DeviceManager.deviceConnecting(uid=payload['uid'])
			if device:
				self._logger.info('Device with uid {} of type {} in room {} connected'.format(device.uid, device.deviceType, device.room))
				managers.MqttServer.publish(topic='projectAlice/devices/connectionAccepted', payload=json.dumps({'siteId': payload['siteId'], 'uid': payload['uid']}))
			else:
				managers.MqttServer.publish(topic='projectAlice/devices/connectionRefused', payload=json.dumps({'siteId': payload['siteId'], 'uid': payload['uid']}))

		elif intent == self._INTENT_ANSWER_YES_OR_NO:
			if session.previousIntent == self._INTENT_REBOOT:
				if 'step' in customData:
					if customData['step'] == 1:
						if commons.isYes(session.message):
							managers.MqttServer.continueDialog(
								sessionId=sessionId,
								text=self.randomTalk('askRebootModules'),
								intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
								previousIntent=self._INTENT_REBOOT,
								customData=json.dumps({
									'module': self.name,
									'step'  : 2
								})
							)
						else:
							managers.MqttServer.endTalk(sessionId, self.randomTalk('abortReboot'))
					else:
						value = 'greet'
						if commons.isYes(session.message):
							value = 'greetAndRebootModules'

						managers.ConfigManager.updateAliceConfiguration('onReboot', value)
						managers.MqttServer.endTalk(sessionId, self.randomTalk('confirmRebooting'))
						managers.ThreadManager.doLater(interval=5, func=self.restart)
				else:
					managers.MqttServer.endTalk(sessionId)
					self._logger.warn('[{}] Asked to reboot, but missing params'.format(self.name))

			elif session.previousIntent == self._INTENT_DUMMY_ADD_USER:
				if commons.isYes(session.message):
					# TODO accesslevel checks!
					managers.UserManager.addNewUser(customData['name'], 'admin')
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addUserWakeword', replace=[customData['name']]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_ADD_WAKEWORD
					)
				else:
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('soWhatsTheName'),
						intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
						previousIntent=self._INTENT_DUMMY_ADD_USER
					)

			elif session.previousIntent == self._INTENT_DUMMY_ADD_WAKEWORD:
				if commons.isYes(session.message):
					managers.WakewordManager.newWakeword(username=customData['name'])
					managers.ThreadManager.newLock('AddingWakeword').set()
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addWakewordAccepted'),
						intentFilter=[self._INTENT_WAKEWORD],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
					)
				else:
					if self.delayed:
						self.delayed = False
						managers.ThreadManager.doLater(interval=2, func=self.onStart)

					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('addWakewordDenied'))
			else:
				return False

		elif intent == self._INTENT_WAKEWORD and session.previousIntent == self._INTENT_DUMMY_WAKEWORD_INSTRUCTION:
			i = 0 # Failsafe...
			while managers.WakewordManager.state != WakewordManagerState.CONFIRMING:
				i += 1
				if i > 15:
					break
				time.sleep(0.5)

			managers.MqttServer.playSound(
				soundFile='/tmp/{}.wav'.format(managers.WakewordManager.getLastSampleNumber()),
				sessionId='checking-wakeword',
				siteId=session.siteId,
				absolutePath=True
			)

			managers.MqttServer.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('howWasTheCapture'),
				intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
				previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
			)

		elif intent == self._INTENT_ANSWER_WAKEWORD_CUTTING:
			if 'more' in slots:
				managers.WakewordManager.trimMore()
			else:
				managers.WakewordManager.trimLess()

			i = 0 # Failsafe
			while managers.WakewordManager.state != WakewordManagerState.CONFIRMING:
				i += 1
				if i > 15:
					break
				time.sleep(0.5)

			managers.MqttServer.playSound(
				soundFile='/tmp/{}.wav'.format(managers.WakewordManager.getLastSampleNumber()),
				sessionId='checking-wakeword',
				siteId=session.siteId,
				absolutePath=True
			)

			managers.MqttServer.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('howWasTheCapture'),
				intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
				previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
			)

		elif intent == self._INTENT_SWITCH_LANGUAGE:
			managers.MqttServer.publish(topic='hermes/asr/textCaptured', payload=json.dumps({'siteId': siteId}))
			if 'ToLang' not in slots:
				managers.MqttServer.endTalk(text=self.randomTalk('noDestinationLanguage'))
				return True

			try:
				managers.LanguageManager.changeActiveLanguage(slots['ToLang'])
				managers.ThreadManager.doLater(interval=3, func=self.langSwitch, args=[slots['ToLang'], siteId, False])
			except LanguageManagerLangNotSupported:
				managers.MqttServer.endTalk(text=self.randomTalk(text='langNotSupported', replace=[slots['ToLang']]))
			except ConfigurationUpdateFailed:
				managers.MqttServer.endTalk(text=self.randomTalk('langSwitchFailed'))

		elif intent == self._INTENT_UPDATE_ALICE:
			if not managers.InternetManager.online:
				managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('noAssistantUpdateOffline'))
				return True

			if 'WhatToUpdate' not in slots:
				update = 1
			else:
				if slots['WhatToUpdate'] == 'alice':
					update = 2
				elif slots['WhatToUpdate'] == 'assistant':
					update = 3
				elif slots['WhatToUpdate'] == 'modules':
					update = 4
				else:
					update = 5

			if update == 1 or update == 5: # All or system
				self._logger.info('[{}] Updating system'.format(self.name))
				managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('confirmAssistantUpdate'))

				def systemUpdate():
					subprocess.run(['sudo', 'apt-get', 'update'])
					subprocess.run(['sudo', 'apt-get', 'dist-upgrade', '-y'])

				managers.ThreadManager.doLater(interval=2, func=systemUpdate)

			if update == 1 or update == 4: # All or modules
				self._logger.info('[{}] Updating modules'.format(self.name))
				managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('confirmAssistantUpdate'))
				managers.ModuleManager.checkForModuleUpdates()

			if update == 1 or update == 2: # All or Alice
				self._logger.info('[{}] Updating Alice'.format(self.name))
				self._logger.info('[{}] Not implemented yet'.format(self.name))
				if update == 2:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('confirmAssistantUpdate'))

			if update == 1 or update == 3: # All or Assistant
				self._logger.info('[{}] Updating assistant'.format(self.name))

				if not managers.LanguageManager.activeSnipsProjectId:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('noProjectIdSet'))
				elif not managers.SnipsConsoleManager.loginCredentialsAreConfigured():
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('bundleUpdateNoCredentials'))
				else:
					if update == 3:
						managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('confirmAssistantUpdate'))

					managers.ThreadManager.doLater(interval=2, func=managers.SamkillaManager.sync)


		elif intent == self._INTENT_REBOOT:
			managers.MqttServer.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('confirmReboot'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_REBOOT,
				customData=json.dumps({
					'module': self.name,
					'step'  : 1
				})
			)

		elif intent == self._INTENT_INVADE_SONOS:
			if 'Room' in slots:
				room = slots['Room']
			else:
				if siteId == 'default':
					room = managers.ConfigManager.getAliceConfigByName('room')
				else:
					room = siteId

			sonosModule = managers.ModuleManager.getModuleInstance('Sonos')
			if not sonosModule:
				managers.MqttServer.endTalk(sessionId, text=self.randomTalk('noActiveModule'))
				return True

			if not sonosModule.anyModuleHere(room):
				managers.MqttServer.endTalk(sessionId, text=self.randomTalk('sorryNoSonosHere'))
			else:
				managers.MqttServer.endTalk(sessionId, text=self.randomTalk('takingOverSonos'))
				time.sleep(4)
				managers.ConfigManager.updateAliceConfiguration('outputOnSonos', '1')
				managers.ConfigManager.updateAliceConfiguration('outputOnSonosIn', room)
				managers.MqttServer.say(text=self.randomTalk('confirmSonosAction'), client=siteId)

		elif intent == self._INTENT_RETREAT:
			managers.MqttServer.endTalk(sessionId, text=self.randomTalk('retreatSonos'))
			time.sleep(2.5)
			managers.ConfigManager.updateAliceConfiguration('outputOnSonos', '0')

		elif intent == self._INTENT_STOP_LISTEN:
			if 'Duration' in slots:
				duration = commons.getDuration(session.message)
				if duration > 0:
					managers.ThreadManager.doLater(interval=duration, func=self.unmuteSite, args=[siteId])

			aliceModule = managers.ModuleManager.getModuleInstance('AliceSatellite')
			if aliceModule:
				aliceModule.notifyDevice('projectAlice/devices/stopListen', siteId=siteId)

			managers.MqttServer.endTalk(sessionId=sessionId)

		elif session.previousIntent == self._INTENT_DUMMY_ADD_USER and (intent == self._INTENT_ANSWER_NAME or intent == self._INTENT_SPELL_WORD):
			if len(managers.UserManager.users) <= 0:
				if intent == self._INTENT_ANSWER_NAME:
					name: str = str(slots['Name']).lower()
					if commons.isSpelledWord(name):
						name = name.replace(' ', '')
				else:
					name = ''
					for slot in slotsObj['Letters']:
						name += slot.value['value']

				if name in managers.UserManager.getAllUserNames(skipGuests=False):
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='userAlreadyExist', replace=[name]),
						intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
						previousIntent=self._INTENT_DUMMY_ADD_USER
					)
				else:
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='confirmUsername', replace=[name]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_ADD_USER,
						customData=json.dumps({
							'name': name
						})
					)
			else:
				managers.MqttServer.endTalk(sessionId)

		return True


	def unmuteSite(self, siteId):
		managers.ModuleManager.getModuleInstance('AliceSatellite').notifyDevice('projectAlice/devices/startListen', siteId=siteId)
		managers.ThreadManager.doLater(interval=1, func=managers.MqttServer.say, args=[self.randomTalk('listeningAgain'), siteId])


	@staticmethod
	def reboot():
		subprocess.run(['sudo', 'reboot'])


	@staticmethod
	def restart():
		subprocess.run(['sudo', 'restart', 'ProjectAlice'])


	def cancelUnregister(self):
		if 'unregisterTimeout' in self._threads:
			thread = self._threads['unregisterTimeout']
			thread.cancel()
			del self._threads['unregisterTimeout']


	def langSwitch(self, newLang: str, siteId: str):
		managers.MqttServer.publish(topic='hermes/asr/textCaptured', payload=json.dumps({'siteId': siteId}))
		subprocess.call([commons.rootDir() + '/system/scripts/langSwitch.sh', newLang])
		managers.ThreadManager.doLater(interval=3, func=self._confirmLangSwitch, args=[newLang, siteId])


	def _confirmLangSwitch(self, siteId: str):
		managers.MqttServer.publish(topic='hermes/leds/onStop', payload=json.dumps({'siteId': siteId}))
		managers.MqttServer.say(text=self.randomTalk('langSwitch'), client=siteId)


	@staticmethod
	def changeFeedbackSound(inDialog: bool):
		if inDialog:
			state = '_ask'
		else:
			state = ''

		subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/system/sounds/{}/start_of_input{}.wav'.format(managers.LanguageManager.activeLanguage, state), commons.rootDir() + '/assistant/custom_dialogue/sound/start_of_input.wav'])
		subprocess.run(['sudo', 'ln', '-sfn', commons.rootDir() + '/system/sounds/{}/error{}.wav'.format(managers.LanguageManager.activeLanguage, state), commons.rootDir() + '/assistant/custom_dialogue/sound/error.wav'])
