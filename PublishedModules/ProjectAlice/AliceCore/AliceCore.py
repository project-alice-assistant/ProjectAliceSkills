import subprocess
import time
from pathlib import Path

import tempfile

from core.ProjectAliceExceptions import ConfigurationUpdateFailed, LanguageManagerLangNotSupported, ModuleStartDelayed
from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import commons, constants
from core.dialog.model.DialogSession import DialogSession
from core.user.model.AccessLevels import AccessLevel
from core.voice.WakewordManager import WakewordManagerState


class AliceCore(Module):
	_INTENT_MODULE_GREETING = 'projectalice/devices/greeting'
	_INTENT_GLOBAL_STOP = Intent('GlobalStop')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_ROOM = Intent('AnswerRoom', isProtected=True)
	_INTENT_SWITCH_LANGUAGE = Intent('SwitchLanguage')
	_INTENT_UPDATE_ALICE = Intent('DoAliceUpdate', isProtected=True)
	_INTENT_REBOOT = Intent('RebootSystem')
	_INTENT_STOP_LISTEN = Intent('StopListening', isProtected=True)
	_INTENT_ADD_DEVICE = Intent('AddComponent')
	_INTENT_ANSWER_HARDWARE_TYPE = Intent('AnswerHardwareType', isProtected=True)
	_INTENT_ANSWER_ESP_TYPE = Intent('AnswerEspType', isProtected=True)
	_INTENT_ANSWER_NAME = Intent('AnswerName', isProtected=True)
	_INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)
	_INTENT_ANSWER_WAKEWORD_CUTTING = Intent('AnswerWakewordCutting', isProtected=True)
	_INTENT_DUMMY_ADD_USER = Intent('DummyAddUser', isProtected=True)
	_INTENT_DUMMY_ADD_WAKEWORD = Intent('DummyAddWakeword', isProtected=True)
	_INTENT_DUMMY_WAKEWORD_INSTRUCTION = Intent('DummyWakewordInstruction', isProtected=True)
	_INTENT_DUMMY_WAKEWORD_FAILED = Intent('DummyWakewordFailed', isProtected=True)
	_INTENT_DUMMY_WAKEWORD_OK = Intent('DummyWakewordOk', isProtected=True)
	_INTENT_DUMMY_ADD_USER_WAKEWORD = Intent('DummyAddUserWakeword', isProtected=True)
	_INTENT_WAKEWORD = Intent('CallWakeword', isProtected=True)
	_INTENT_ADD_USER = Intent('AddNewUser', isProtected=True)
	_INTENT_ANSWER_ACCESSLEVEL = Intent('AnswerAccessLevel', isProtected=True)


	def __init__(self):
		self._INTENTS = {
			self._INTENT_GLOBAL_STOP: self.onMessage,
			self._INTENT_MODULE_GREETING: self.deviceGreetingIntent,
			self._INTENT_ANSWER_YES_OR_NO: self.answerYesOrNoIntent,
			self._INTENT_ANSWER_ROOM: self.onMessage,
			self._INTENT_SWITCH_LANGUAGE: self.onMessage,
			self._INTENT_UPDATE_ALICE: self.aliceUpdateIntent,
			self._INTENT_REBOOT: self.onMessage,
			self._INTENT_STOP_LISTEN: self.onMessage,
			self._INTENT_ADD_DEVICE: self.addDeviceIntent,
			self._INTENT_ANSWER_HARDWARE_TYPE: self.onMessage,
			self._INTENT_ANSWER_ESP_TYPE: self.onMessage,
			self._INTENT_ANSWER_NAME: self.onMessage,
			self._INTENT_SPELL_WORD: self.onMessage,
			self._INTENT_DUMMY_ADD_USER: self.onMessage,
			self._INTENT_DUMMY_ADD_WAKEWORD: self.onMessage,
			self._INTENT_DUMMY_WAKEWORD_INSTRUCTION: self.onMessage,
			self._INTENT_DUMMY_WAKEWORD_FAILED: self.onMessage,
			self._INTENT_ANSWER_WAKEWORD_CUTTING: self.onMessage,
			self._INTENT_DUMMY_WAKEWORD_OK: self.onMessage,
			self._INTENT_WAKEWORD: self.onMessage,
			self._INTENT_ADD_USER: self.onMessage,
			self._INTENT_ANSWER_ACCESSLEVEL: self.onMessage
		}

		self._AUTH_ONLY_INTENTS = {
			self._INTENT_ADD_USER: 'admin',
			self._INTENT_ADD_DEVICE: 'admin',
			self._INTENT_UPDATE_ALICE: 'default',
			self._INTENT_REBOOT: 'default'
		}

		self._INTENT_ANSWER_YES_OR_NO.dialogMapping = {
			self._INTENT_REBOOT: {
				0: self.confirmReboot,
				1: self.reboot
			}
		}

		self._threads = dict()
		super().__init__(self._INTENTS, authOnlyIntents=self._AUTH_ONLY_INTENTS)


	def onStart(self):
		super().onStart()
		self.changeFeedbackSound(inDialog=False)

		if not self.UserManager.users:
			if not self.delayed:
				self.logWarning('No user found in database')
				raise ModuleStartDelayed(self.name)
			else:
				self._addFirstUser()

		return self._INTENTS


	def _addFirstUser(self):
		self.ask(
			text=self.randomTalk('addAdminUser'),
			intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
			previousIntent=self._INTENT_DUMMY_ADD_USER,
			canBeEnqueued=False
		)


	def onUserCancel(self, session: DialogSession):
		if self.delayed: # type: ignore
			self.delayed = False

			if not self.ThreadManager.getEvent('AddingWakeword').isSet():
				self.say(text=self.randomTalk('noStartWithoutAdmin'), siteId=session.siteId)

				def stop():
					subprocess.run(['sudo', 'systemctl', 'stop', 'ProjectAlice'])

				self.ThreadManager.doLater(interval=10, func=stop)
			else:
				self.ThreadManager.getEvent('AddingWakeword').clear()
				self.say(text=self.randomTalk('cancellingWakewordCapture'), siteId=session.siteId)
				self.ThreadManager.doLater(interval=2, func=self.onStart)


	def onSessionTimeout(self, session: DialogSession):
		if self.delayed:
			if not self.UserManager.users:
				self._addFirstUser()
			else:
				self.delayed = False


	def onSessionError(self, session: DialogSession):
		if self.delayed:
			if not self.UserManager.users:
				self._addFirstUser()
			else:
				self.delayed = False


	def onSessionStarted(self, session: DialogSession):
		self.changeFeedbackSound(inDialog=True, siteId=session.siteId)


	def onSessionEnded(self, session: DialogSession):
		if not self.ThreadManager.getEvent('AddingWakeword').isSet():
			self.changeFeedbackSound(inDialog=False, siteId=session.siteId)

			if self.delayed:
				if not self.UserManager.users:
					self._addFirstUser()
				else:
					self.delayed = False


	def onSleep(self):
		self.MqttManager.toggleFeedbackSounds('off')


	def onWakeup(self):
		self.MqttManager.toggleFeedbackSounds('on')


	def onBooted(self):
		if not super().onBooted():
			return

		onReboot = self.ConfigManager.getAliceConfigByName('onReboot')
		if onReboot:
			if onReboot == 'greet':
				self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('confirmRebooted'), 'all'])
			elif onReboot == 'greetAndRebootModules':
				self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('confirmRebootingModules'), 'all'])
			else:
				self.logWarning('onReboot config has an unknown value')

			self.ConfigManager.updateAliceConfiguration('onReboot', '')


	def onGoingBed(self):
		self.UserManager.goingBed()


	def onLeavingHome(self):
		self.UserManager.leftHome()


	def onReturningHome(self):
		self.UserManager.home()


	def onSayFinished(self, session: DialogSession):
		if self.ThreadManager.getEvent('AddingWakeword').isSet() and self.WakewordManager.state == WakewordManagerState.IDLE:
			self.ThreadManager.doLater(interval=0.5, func=self.WakewordManager.addASample)


	def onSnipsAssistantInstalled(self):
		self.say(text=self.randomTalk('confirmBundleUpdate'))


	def onSnipsAssistantFailedInstalling(self):
		self.say(text=self.randomTalk('bundleUpdateFailed'))


	def onSnipsAssistantDownloadFailed(self):
		self.say(text=self.randomTalk('bundleUpdateFailed'))


	def addDeviceIntent(self, intent: str, session: DialogSession) -> bool:
		if self.DeviceManager.isBusy():
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('busy'),
				siteId=session.siteId
			)
			return True

		if 'Hardware' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatHardware'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				previousIntent=self._INTENT_ADD_DEVICE
			)
			return True

		elif session.slotsAsObjects['Hardware'][0].value['value'] == 'esp' and 'EspType' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatESP'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				previousIntent=self._INTENT_ADD_DEVICE
			)
			return True

		elif 'Room' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whichRoom'),
				intentFilter=[self._INTENT_ANSWER_ROOM],
				previousIntent=self._INTENT_ADD_DEVICE
			)
			return True

		hardware = session.slotsAsObjects['Hardware'][0].value['value']
		if hardware == 'esp':
			if not self.ModuleManager.isModuleActive('Tasmota'):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('requireTasmotaModule'))
				return True

			if self.DeviceManager.isBusy():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
				return True

			if not self.DeviceManager.startTasmotaFlashingProcess(commons.cleanRoomNameToSiteId(session.slots['Room']), session.slotsAsObjects['EspType'][0].value['value'], session):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('espFailed'))

		elif hardware == 'satellite':
			if self.DeviceManager.startBroadcastingForNewDevice(commons.cleanRoomNameToSiteId(session.slots['Room']), session.siteId):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmDeviceAddingMode'))
			else:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
		else:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('unknownHardware'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE],
				previousIntent=self._INTENT_ADD_DEVICE
			)
			return True


	def deviceGreetingIntent(self, intent: str, session: DialogSession) -> bool:
		if 'uid' not in session.payload or 'siteId' not in session.payload:
			self.logWarning('A device tried to connect but is missing informations in the payload, refused')
			self.publish(topic='projectalice/devices/connectionRefused', payload={'siteId': session.payload['siteId']})
			return True

		device = self.DeviceManager.deviceConnecting(uid=session.payload['uid'])
		if device:
			self.logInfo(f'Device with uid {device.uid} of type {device.deviceType} in room {device.room} connected')
			self.publish(topic='projectalice/devices/connectionAccepted', payload={'siteId': session.payload['siteId'], 'uid': session.payload['uid']})
		else:
			self.publish(topic='projectalice/devices/connectionRefused', payload={'siteId': session.payload['siteId'], 'uid': session.payload['uid']})
			return True


	def answerYesOrNoIntent(self, intent: str, session: DialogSession) -> bool:
		pass


	def aliceUpdateIntent(self, intent: str, session: DialogSession) -> bool:
		if not self.InternetManager.online:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('noAssistantUpdateOffline'))
			return True

		self.publish('hermes/leds/systemUpdate')

		if 'WhatToUpdate' not in session.slots:
			update = 1
		elif session.slots['WhatToUpdate'] == 'alice':
			update = 2
		elif session.slots['WhatToUpdate'] == 'assistant':
			update = 3
		elif session.slots['WhatToUpdate'] == 'modules':
			update = 4
		else:
			update = 5

		if update in {1, 5}:  # All or system
			self.logInfo('Updating system')
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmAssistantUpdate'))


			def systemUpdate():
				subprocess.run(['sudo', 'apt-get', 'update'])
				subprocess.run(['sudo', 'apt-get', 'dist-upgrade', '-y'])
				subprocess.run(['git', 'stash'])
				subprocess.run(['git', 'pull'])
				subprocess.run(['git', 'stash', 'clear'])
				SuperManager.getInstance().threadManager.doLater(interval=2, func=subprocess.run, args=['sudo', 'systemctl', 'restart', 'ProjectAlice'])


			self.ThreadManager.doLater(interval=2, func=systemUpdate)

		if update in {1, 4}:  # All or modules
			self.logInfo('Updating modules')
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmAssistantUpdate'))
			self.ModuleManager.checkForModuleUpdates()

		if update in {1, 2}:  # All or Alice
			self.logInfo('Updating Alice')
			if update == 2:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmAssistantUpdate'))

		if update in {1, 3}:  # All or Assistant
			self.logInfo('Updating assistant')

			if not self.LanguageManager.activeSnipsProjectId:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('noProjectIdSet'))
			elif not self.SnipsConsoleManager.loginCredentialsAreConfigured():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('bundleUpdateNoCredentials'))
			else:
				if update == 3:
					self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmAssistantUpdate'))

				self.ThreadManager.doLater(interval=2, func=self.SamkillaManager.sync)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if intent == self._INTENT_GLOBAL_STOP:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmGlobalStop'), siteId=session.siteId)
			return True

		siteId = session.siteId
		slots = session.slots
		slotsObj = session.slotsAsObjects
		sessionId = session.sessionId
		customData = session.customData

		if intent == self._INTENT_ANSWER_YES_OR_NO:
			if session.previousIntent == self._INTENT_REBOOT:
				if 'step' in customData:
					if customData['step'] == 1:
						if commons.isYes(session):
							self.continueDialog(
								sessionId=sessionId,
								text=self.randomTalk('askRebootModules'),
								intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
								previousIntent=self._INTENT_REBOOT,
								customData={
									'module': self.name,
									'step'  : 2
								}
							)
						else:
							self.endDialog(sessionId, self.randomTalk('abortReboot'))
					else:
						value = 'greet'
						if commons.isYes(session):
							value = 'greetAndRebootModules'

						self.ConfigManager.updateAliceConfiguration('onReboot', value)
						self.endDialog(sessionId, self.randomTalk('confirmRebooting'))
						self.ThreadManager.doLater(interval=5, func=self.restart)
				else:
					self.endDialog(sessionId)
					self.logWarning('Asked to reboot, but missing params')

			elif session.previousIntent == self._INTENT_DUMMY_ADD_USER:
				if commons.isYes(session):
					self.UserManager.addNewUser(customData['name'], AccessLevel.ADMIN.name.lower())
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addUserWakeword', replace=[customData['name']]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_ADD_WAKEWORD
					)
				else:
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('soWhatsTheName'),
						intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
						previousIntent=self._INTENT_DUMMY_ADD_USER
					)

			elif session.previousIntent == self._INTENT_DUMMY_ADD_WAKEWORD:
				if commons.isYes(session):
					self.WakewordManager.newWakeword(username=customData['name'])
					self.ThreadManager.newEvent('AddingWakeword').set()
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addWakewordAccepted'),
						intentFilter=[self._INTENT_WAKEWORD],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
					)
				else:
					if self.delayed:
						self.delayed = False
						self.ThreadManager.doLater(interval=2, func=self.onStart)

					self.endDialog(sessionId=sessionId, text=self.randomTalk('addWakewordDenied'))

			elif session.previousIntent == self._INTENT_ADD_USER:
				if commons.isYes(session):
					self.UserManager.addNewUser(customData['username'], slots['UserAccessLevel'])
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addUserWakeword', replace=[slots['Name'], slots['UserAccessLevel']]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_ADD_USER_WAKEWORD
					)
				else:
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('soWhatsTheName'),
						intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
						previousIntent=self._INTENT_ADD_USER
					)

			elif session.previousIntent == self._INTENT_DUMMY_ADD_USER_WAKEWORD:
				if commons.isYes(session):
					self.WakewordManager.newWakeword(username=customData['username'])
					self.ThreadManager.newEvent('AddingWakeword').set()
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='addUserAddWakewordAccepted', replace=[customData['username']]),
						intentFilter=[self._INTENT_WAKEWORD],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
					)
					return True
				else:
					self.endDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='addUserAddWakewordDenied', replace=[customData['username'], customData['username']])
					)

			elif session.previousIntent == self._INTENT_DUMMY_WAKEWORD_FAILED:
				if commons.isYes(session):
					self.WakewordManager.tryCaptureFix()
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('addWakewordAccepted'),
						intentFilter=[self._INTENT_WAKEWORD],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
					)
				else:
					if self.delayed:
						self.delayed = False
						self.ThreadManager.getEvent('AddingWakeword').clear()
						self.ThreadManager.doLater(interval=2, func=self.onStart)

					self.endDialog(sessionId=sessionId, text=self.randomTalk('cancellingWakewordCapture'))

			else:
				return False

		elif intent == self._INTENT_WAKEWORD and session.previousIntent == self._INTENT_DUMMY_WAKEWORD_INSTRUCTION:
			i = 0 # Failsafe...
			while self.WakewordManager.state != WakewordManagerState.CONFIRMING:
				i += 1
				if i > 15:
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('wakewordCaptureTooNoisy'),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_FAILED
					)
					return True
				time.sleep(0.5)

			filepath = Path(tempfile.gettempdir(), str(self.WakewordManager.getLastSampleNumber())).with_suffix('.wav')

			if not filepath.exists():
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('wakewordCaptureFailed'),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_DUMMY_WAKEWORD_FAILED
				)
			else:
				self.playSound(
					soundFilename=str(self.WakewordManager.getLastSampleNumber()),
					location=Path(tempfile.gettempdir()),
					sessionId='checking-wakeword',
					siteId=session.siteId
				)

				text = 'howWasTheCapture' if self.WakewordManager.getLastSampleNumber() == 1 else 'howWasThisCapture'

				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk(text),
					intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
					slot='WakewordCaptureResult',
					previousIntent=self._INTENT_WAKEWORD
				)

		elif intent == self._INTENT_ANSWER_WAKEWORD_CUTTING:
			if session.slotValue('WakewordCaptureResult') == 'more':
				self.WakewordManager.trimMore()
			elif session.slotValue('WakewordCaptureResult') == 'less':
				self.WakewordManager.trimLess()
			elif session.slotValue('WakewordCaptureResult') == 'restart':
				self.WakewordManager.state = WakewordManagerState.IDLE
				self.WakewordManager.removeSample()
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('restartSample'),
					intentFilter=[self._INTENT_WAKEWORD],
					previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
				)

				return True
			elif session.slotValue('WakewordCaptureResult') == 'ok':
				if self.WakewordManager.getLastSampleNumber() < 3:
					self.WakewordManager.state = WakewordManagerState.IDLE
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('sampleOk', replace=[3 - self.WakewordManager.getLastSampleNumber()]),
						intentFilter=[self._INTENT_WAKEWORD],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_INSTRUCTION
					)
				else:
					self.endSession(sessionId)
					self.ThreadManager.doLater(interval=1, func=self.WakewordManager.finalizeWakeword)

					self.ThreadManager.getEvent('AddingWakeword').clear()
					if self.delayed:
						self.delayed = False
						self.ThreadManager.doLater(interval=2, func=self.onStart)
						self.ThreadManager.doLater(interval=6, func=self.say, args=[self.randomTalk('wakewordCaptureDone'), session.siteId])

				return True

			i = 0 # Failsafe
			while self.WakewordManager.state != WakewordManagerState.CONFIRMING:
				i += 1
				if i > 15:
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk('wakewordCaptureTooNoisy'),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_WAKEWORD_FAILED
					)
					return True
				time.sleep(0.5)

			self.playSound(
				soundFilename=str(self.WakewordManager.getLastSampleNumber()),
				location=Path(tempfile.gettempdir()),
				sessionId='checking-wakeword',
				siteId=session.siteId
			)

			self.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('howWasTheCaptureNow'),
				intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
				slot='WakewordCaptureResult',
				previousIntent=self._INTENT_WAKEWORD
			)

		elif intent == self._INTENT_SWITCH_LANGUAGE:
			self.publish(topic='hermes/asr/textCaptured', payload={'siteId': siteId})
			if 'ToLang' not in slots:
				self.endDialog(text=self.randomTalk('noDestinationLanguage'))
				return True

			try:
				self.LanguageManager.changeActiveLanguage(slots['ToLang'])
				self.ThreadManager.doLater(interval=3, func=self.langSwitch, args=[slots['ToLang'], siteId])
			except LanguageManagerLangNotSupported:
				self.endDialog(text=self.randomTalk(text='langNotSupported', replace=[slots['ToLang']]))
			except ConfigurationUpdateFailed:
				self.endDialog(text=self.randomTalk('langSwitchFailed'))


		elif intent == self._INTENT_REBOOT:
			self.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('confirmReboot'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_REBOOT,
				customData={
					'module': self.name,
					'step'  : 1
				}
			)

		elif intent == self._INTENT_STOP_LISTEN:
			if 'Duration' in slots:
				duration = commons.getDuration(session)
				if duration > 0:
					self.ThreadManager.doLater(interval=duration, func=self.unmuteSite, args=[siteId])

			aliceModule = self.ModuleManager.getModuleInstance('AliceSatellite')
			if aliceModule:
				aliceModule.notifyDevice('projectalice/devices/stopListen', siteId=siteId)

			self.endDialog(sessionId=sessionId)

		elif session.previousIntent == self._INTENT_DUMMY_ADD_USER and intent in {self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD}:
			if not self.UserManager.users:
				if intent == self._INTENT_ANSWER_NAME:
					name: str = str(slots['Name']).lower()
					if commons.isSpelledWord(name):
						name = name.replace(' ', '')
				else:
					name = ''.join([slot.value['value'] for slot in slotsObj['Letters']])

				if name in self.UserManager.getAllUserNames(skipGuests=False):
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='userAlreadyExist', replace=[name]),
						intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
						previousIntent=self._INTENT_DUMMY_ADD_USER
					)
				else:
					self.continueDialog(
						sessionId=sessionId,
						text=self.randomTalk(text='confirmUsername', replace=[name]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_DUMMY_ADD_USER,
						customData={
							'name': name
						}
					)
			else:
				self.endDialog(sessionId)

		elif intent in {self._INTENT_ADD_USER, self._INTENT_ANSWER_ACCESSLEVEL}  or session.previousIntent == self._INTENT_ADD_USER and intent != self._INTENT_SPELL_WORD:
			if 'Name' not in slots:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('addUserWhatsTheName'),
					intentFilter=[self._INTENT_ANSWER_NAME],
					previousIntent=self._INTENT_ADD_USER,
					slot='Name'
				)
				return True

			if session.slotRawValue('Name') == constants.UNKNOWN_WORD:
				self.continueDialog(
					sessionId=sessionId,
					text=self.TalkManager.randomTalk('notUnderstood', module='system'),
					intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
					previousIntent=self._INTENT_ADD_USER
				)
				return True

			if slots['Name'] in self.UserManager.getAllUserNames(skipGuests=False):
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk(text='userAlreadyExist', replace=[slots['Name']]),
					intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
					previousIntent=self._INTENT_ADD_USER
				)
				return True

			if 'UserAccessLevel' not in slots:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('addUserWhatAccessLevel'),
					intentFilter=[self._INTENT_ANSWER_ACCESSLEVEL],
					previousIntent=self._INTENT_ADD_USER,
					slot='UserAccessLevel'
				)
				return True

			self.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk(text='addUserConfirmUsername', replace=[slots['Name']]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_ADD_USER,
				customData={
					'username': slots['Name']
				}
			)
			return True

		elif intent == self._INTENT_SPELL_WORD and session.previousIntent == self._INTENT_ADD_USER:
			name = ''.join([slot.value['value'] for slot in slotsObj['Letters']])

			session.slots['Name']['value'] = name
			if name in self.UserManager.getAllUserNames(skipGuests=False):
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk(text='userAlreadyExist', replace=[name]),
					intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
					previousIntent=self._INTENT_ADD_USER
				)
			else:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk(text='addUserConfirmUsername', replace=[name]),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_ADD_USER,
					customData={
						'username': name
					}
				)

		return True


	def unmuteSite(self, siteId):
		self.ModuleManager.getModuleInstance('AliceSatellite').notifyDevice('projectalice/devices/startListen', siteId=siteId)
		self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('listeningAgain'), siteId])


	@staticmethod
	def reboot():
		subprocess.run(['sudo', 'shutdown', '-r', 'now'])


	@staticmethod
	def restart():
		subprocess.run(['sudo', 'systemctl', 'restart', 'ProjectAlice'])


	def cancelUnregister(self):
		if 'unregisterTimeout' in self._threads:
			thread = self._threads['unregisterTimeout']
			thread.cancel()
			del self._threads['unregisterTimeout']


	def langSwitch(self, newLang: str, siteId: str):
		self.publish(topic='hermes/asr/textCaptured', payload={'siteId': siteId})
		subprocess.run([f'{commons.rootDir()}/system/scripts/langSwitch.sh', newLang])
		self.ThreadManager.doLater(interval=3, func=self._confirmLangSwitch, args=[siteId])


	def _confirmLangSwitch(self, siteId: str):
		self.publish(topic='hermes/leds/onStop', payload={'siteId': siteId})
		self.say(text=self.randomTalk('langSwitch'), siteId=siteId)


	# noinspection PyUnusedLocal
	def changeFeedbackSound(self, inDialog: bool, siteId: str = 'all'):
		if not Path(commons.rootDir(), 'assistant').exists():
			return

		# Unfortunately we can't yet get rid of the feedback sound because Alice hears herself finishing the sentence and capturing part of it
		if inDialog:
			state = '_ask'
		else:
			state = ''

		subprocess.run(['sudo', 'ln', '-sfn', f'{commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/start_of_input{state}.wav', f'{commons.rootDir()}/assistant/custom_dialogue/sound/start_of_input.wav'])
		subprocess.run(['sudo', 'ln', '-sfn', f'{commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/error{state}.wav', f'{commons.rootDir()}/assistant/custom_dialogue/sound/error.wav'])
