import subprocess
import time
from pathlib import Path

import tempfile

from core.ProjectAliceExceptions import ModuleStartDelayed
from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import Commons, constants
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
	_INTENT_WAKEWORD = Intent('CallWakeword', isProtected=True)
	_INTENT_ADD_USER = Intent('AddNewUser', isProtected=True)
	_INTENT_ANSWER_ACCESSLEVEL = Intent('AnswerAccessLevel', isProtected=True)
	_INTENT_ANSWER_NUMBER = Intent('AnswerNumber', isProtected=True)


	def __init__(self):
		self._INTENTS = [
			self._INTENT_GLOBAL_STOP,
			(self._INTENT_MODULE_GREETING, self.deviceGreetingIntent),
			self._INTENT_ANSWER_YES_OR_NO,
			(self._INTENT_ANSWER_ROOM, self.addDeviceIntent),
			self._INTENT_SWITCH_LANGUAGE,
			(self._INTENT_UPDATE_ALICE, self.aliceUpdateIntent),
			(self._INTENT_REBOOT, self.confirmReboot),
			(self._INTENT_STOP_LISTEN, self.stopListenIntent),
			(self._INTENT_ADD_DEVICE, self.addDeviceIntent),
			(self._INTENT_ANSWER_HARDWARE_TYPE, self.addDeviceIntent),
			(self._INTENT_ANSWER_ESP_TYPE, self.addDeviceIntent),
			self._INTENT_ANSWER_NUMBER,
			self._INTENT_ANSWER_NAME,
			self._INTENT_SPELL_WORD,
			(self._INTENT_ANSWER_WAKEWORD_CUTTING, self.confirmWakewordTrimming),
			(self._INTENT_WAKEWORD, self.confirmWakeword),
			(self._INTENT_ADD_USER, self.addNewUser),
			self._INTENT_ANSWER_ACCESSLEVEL
		]

		self._AUTH_ONLY_INTENTS = {
			self._INTENT_ADD_USER: AccessLevel.ADMIN,
			self._INTENT_ADD_DEVICE: AccessLevel.ADMIN,
			self._INTENT_UPDATE_ALICE: AccessLevel.DEFAULT,
			self._INTENT_REBOOT: AccessLevel.DEFAULT
		}

		self._INTENT_ANSWER_YES_OR_NO.dialogMapping = {
			'confirmingReboot': self.confirmModuleReboot,
			'confirmingModuleReboot': self.reboot,
			'confirmingUsername': self.checkUsername,
			'confirmingWakewordCreation': self.createWakeword,
			'confirmingRecaptureAfterFailure': self.tryFixAndRecapture,
			'confirmingPinCode': self.askCreateWakeword
		}

		self._INTENT_ANSWER_ACCESSLEVEL.dialogMapping = {
			'confirmingUsername': self.checkUsername
		}

		self._INTENT_ANSWER_NAME.dialogMapping = {
			'addingUser': self.confirmUsername
		}

		self._INTENT_SPELL_WORD.dialogMapping = {
			'addingUser': self.confirmUsername
		}

		self._INTENT_ANSWER_NUMBER.dialogMapping = {
			'addingPinCode': self.addUserPinCode
		}

		self._threads = dict()
		super().__init__(self._INTENTS, authOnlyIntents=self._AUTH_ONLY_INTENTS)


	def addNewUser(self, session: DialogSession, **_kwargs):
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('addUserWhatsTheName'),
			intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
			currentDialogState='addingUser'
		)


	def askCreateWakeword(self, session: DialogSession, **_kwargs):
		if 'pinCode' in session.customData:
			if Commons.isYes(session):
				self.UserManager.addNewUser(name=session.customData['username'], access=session.customData['accessLevel'], pinCode=session.customData['pinCode'])
			else:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('addWrongPin'),
					intentFilter=[self._INTENT_ANSWER_NUMBER],
					currentDialogState='addingPinCode'
				)
				return

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('addUserWakeword', replace=[session.customData['username']]),
			intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
			currentDialogState='confirmingWakewordCreation'
		)


	def addUserPinCode(self, session: DialogSession, **_kwargs):
		if 'Number' not in session.slotsAsObjects:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', module='system'),
				intentFilter=[self._INTENT_ANSWER_NUMBER],
				currentDialogState='addingPinCode'
			)
			return
		else:
			pin = ''
			for number in session.slotsAsObjects['Number']:
				pin += str(int(number.value['value']))

			if len(pin) != 4:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('addPinInvalid'),
					intentFilter=[self._INTENT_ANSWER_NUMBER],
					currentDialogState='addingPinCode'
				)
			else:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('addPinConfirm', replace=[digit for digit in pin]),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					currentDialogState='confirmingPinCode',
					customData={
						'pinCode': int(pin)
					}
				)


	def confirmWakewordTrimming(self, session: DialogSession, **_kwargs):
		if session.slotValue('WakewordCaptureResult') == 'more':
			self.WakewordManager.trimMore()

		elif session.slotValue('WakewordCaptureResult') == 'less':
			self.WakewordManager.trimLess()

		elif session.slotValue('WakewordCaptureResult') == 'restart':
			self.WakewordManager.state = WakewordManagerState.IDLE
			self.WakewordManager.removeSample()
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('restartSample'),
				intentFilter=[self._INTENT_WAKEWORD]
			)

			return

		elif session.slotValue('WakewordCaptureResult') == 'ok':
			if self.WakewordManager.getLastSampleNumber() < 3:
				self.WakewordManager.state = WakewordManagerState.IDLE
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('sampleOk', replace=[3 - self.WakewordManager.getLastSampleNumber()]),
					intentFilter=[self._INTENT_WAKEWORD]
				)
			else:
				self.endSession(session.sessionId)
				self.ThreadManager.doLater(interval=1, func=self.WakewordManager.finalizeWakeword)

				self.ThreadManager.getEvent('AddingWakeword').clear()
				if self.delayed:
					self.delayed = False
					self.ThreadManager.doLater(interval=2, func=self.onStart)

				self.ThreadManager.doLater(interval=4, func=self.say, args=[self.randomTalk('wakewordCaptureDone'), session.siteId])

			return

		i = 0  # Failsafe
		while self.WakewordManager.state != WakewordManagerState.CONFIRMING:
			i += 1
			if i > 15:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('wakewordCaptureTooNoisy'),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					currentDialogState='confirmingRecaptureAfterFailure'
				)
				return
			time.sleep(0.5)

		self.playSound(
			soundFilename=str(self.WakewordManager.getLastSampleNumber()),
			location=Path(tempfile.gettempdir()),
			sessionId='checking-wakeword',
			siteId=session.siteId
		)

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('howWasTheCaptureNow'),
			intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
			slot='WakewordCaptureResult'
		)


	def tryFixAndRecapture(self, intent: str, session: DialogSession):
		if Commons.isYes(session):
			self.WakewordManager.tryCaptureFix()
			return self.confirmWakewordTrimming(intent=intent, session=session)
		else:
			if self.delayed:
				self.delayed = False
				self.ThreadManager.getEvent('AddingWakeword').clear()
				self.ThreadManager.doLater(interval=2, func=self.onStart)

			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('cancellingWakewordCapture'))


	def confirmWakeword(self, session: DialogSession, **_kwargs):
		i = 0  # Failsafe...
		while self.WakewordManager.state != WakewordManagerState.CONFIRMING:
			i += 1
			if i > 15:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('wakewordCaptureTooNoisy'),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					currentDialogState='confirmingRecaptureAfterFailure'
				)
				return True
			time.sleep(0.5)

		filepath = Path(tempfile.gettempdir(), str(self.WakewordManager.getLastSampleNumber())).with_suffix('.wav')

		if not filepath.exists():
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('wakewordCaptureFailed'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState='confirmingRecaptureAfterFailure'
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
				sessionId=session.sessionId,
				text=self.randomTalk(text),
				intentFilter=[self._INTENT_ANSWER_WAKEWORD_CUTTING],
				slot='WakewordCaptureResult',
				currentDialogState='confirmingCaptureResult'
			)


	def createWakeword(self, session: DialogSession, **_kwargs):
		if Commons.isYes(session):
			self.WakewordManager.newWakeword(username=session.customData['username'])
			self.ThreadManager.newEvent('AddingWakeword').set()

			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('addWakewordAccepted'),
				intentFilter=[self._INTENT_WAKEWORD]
			)
		else:
			if self.delayed:
				self.delayed = False
				self.ThreadManager.doLater(interval=2, func=self.onStart)

			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('addWakewordDenied'))


	def checkUsername(self, session: DialogSession, **_kwargs):
		if Commons.isYes(session):
			if session.customData['username'] in self.UserManager.getAllUserNames(skipGuests=False):
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text='userAlreadyExist', replace=[session.slots['Name']]),
					intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
					currentDialogState='addingUser'
				)
				return

			if 'UserAccessLevel' not in session.slots and 'UserAccessLevel' not in session.customData:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('addUserWhatAccessLevel'),
					intentFilter=[self._INTENT_ANSWER_ACCESSLEVEL],
					currentDialogState='confirmingUsername',
					slot='UserAccessLevel'
				)
				return

			elif 'UserAccessLevel' in session.slots:
				accessLevel = session.slots['UserAccessLevel']

			else:
				accessLevel = session.customData['UserAccessLevel']

			if accessLevel.lower() == AccessLevel.ADMIN.name.lower():
				text = 'addAdminPin'
			else:
				text = 'addUserPin'

			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text),
				intentFilter=[self._INTENT_ANSWER_NUMBER],
				currentDialogState='addingPinCode',
				customData={
					'accessLevel': accessLevel
				}
			)

		else:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('soWhatsTheName'),
				intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
				currentDialogState='addingUser'
			)


	def confirmUsername(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_NAME:
			username = str(session.slots['Name']).lower()
			if Commons.isSpelledWord(username):
				username = username.replace(' ', '')
		else:
			username = ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])

		if session.slotRawValue('Name') == constants.UNKNOWN_WORD:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', module='system'),
				intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
				currentDialogState='addingUser'
			)
			return

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='confirmUsername', replace=[username]),
			intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
			currentDialogState='confirmingUsername',
			customData={
				'username': username
			}
		)


	def stopListenIntent(self, session: DialogSession, **_kwargs):
		if 'Duration' in session.slots:
			duration = Commons.getDuration(session)
			if duration > 0:
				self.ThreadManager.doLater(interval=duration, func=self.unmuteSite, args=[session.siteId])

		aliceModule = self.ModuleManager.getModuleInstance('AliceSatellite')
		if aliceModule:
			aliceModule.notifyDevice('projectalice/devices/stopListen', siteId=session.siteId)

		self.endDialog(sessionId=session.sessionId)


	def addDeviceIntent(self, session: DialogSession, **_kwargs):
		if self.DeviceManager.isBusy():
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('busy'),
				siteId=session.siteId
			)
			return

		if 'Hardware' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatHardware'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				currentDialogState='specifyingHardware'
			)
			return

		elif session.slotsAsObjects['Hardware'][0].value['value'] == 'esp' and 'EspType' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatESP'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				currentDialogState='specifyingEspType'
			)
			return

		elif 'Room' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whichRoom'),
				intentFilter=[self._INTENT_ANSWER_ROOM],
				currentDialogState='specifyingRoom'
			)
			return

		hardware = session.slotsAsObjects['Hardware'][0].value['value']
		if hardware == 'esp':
			if not self.ModuleManager.isModuleActive('Tasmota'):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('requireTasmotaModule'))
				return

			if self.DeviceManager.isBusy():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
				return

			if not self.DeviceManager.startTasmotaFlashingProcess(Commons.cleanRoomNameToSiteId(session.slots['Room']), session.slotsAsObjects['EspType'][0].value['value'], session):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('espFailed'))

		elif hardware == 'zigbee':
			if not self.ModuleManager.isModuleActive('Zigbee2Mqtt'):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('requireZigbeeModule'))
				return

			if self.DeviceManager.isBusy():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
				return

			self.DeviceManager.addZigBeeDevice()

		elif hardware == 'satellite':
			if self.DeviceManager.startBroadcastingForNewDevice(Commons.cleanRoomNameToSiteId(session.slots['Room']), session.siteId):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmDeviceAddingMode'))
			else:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
		else:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('unknownHardware'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE],
				currentDialogState='specifyingHardware'
			)


	def confirmReboot(self, session: DialogSession, **_kwargs):
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('confirmReboot'),
			intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
			currentDialogState='confirmingReboot'
		)


	def confirmModuleReboot(self, session: DialogSession, **_kwargs):
		if Commons.isYes(session):
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('askRebootModules'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState='confirmingModuleReboot'
			)
		else:
			self.endDialog(session.sessionId, self.randomTalk('abortReboot'))


	def reboot(self, session: DialogSession, **_kwargs):
		value = 'greet'
		if Commons.isYes(session):
			value = 'greetAndRebootModules'

		self.ConfigManager.updateAliceConfiguration('onReboot', value)
		self.endDialog(session.sessionId, self.randomTalk('confirmRebooting'))
		self.ThreadManager.doLater(interval=5, func=subprocess.run, args=[['sudo', 'shutdown', '-r', 'now']])


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
			canBeEnqueued=False,
			currentDialogState='addingUser',
			customData={
				'UserAccessLevel': 'admin'
			}
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


	def deviceGreetingIntent(self, session: DialogSession, **_kwargs) -> bool:
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


	def aliceUpdateIntent(self, session: DialogSession, **_kwargs) -> bool:
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

		return True


	def unmuteSite(self, siteId):
		self.ModuleManager.getModuleInstance('AliceSatellite').notifyDevice('projectalice/devices/startListen', siteId=siteId)
		self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('listeningAgain'), siteId])


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
		subprocess.run([f'{Commons.rootDir()}/system/scripts/langSwitch.sh', newLang])
		self.ThreadManager.doLater(interval=3, func=self._confirmLangSwitch, args=[siteId])


	def _confirmLangSwitch(self, siteId: str):
		self.publish(topic='hermes/leds/onStop', payload={'siteId': siteId})
		self.say(text=self.randomTalk('langSwitch'), siteId=siteId)


	# noinspection PyUnusedLocal
	def changeFeedbackSound(self, inDialog: bool, siteId: str = 'all'):
		if not Path(Commons.rootDir(), 'assistant').exists():
			return

		# Unfortunately we can't yet get rid of the feedback sound because Alice hears herself finishing the sentence and capturing part of it
		if inDialog:
			state = '_ask'
		else:
			state = ''

		subprocess.run(['sudo', 'ln', '-sfn', f'{Commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/start_of_input{state}.wav', f'{Commons.rootDir()}/assistant/custom_dialogue/sound/start_of_input.wav'])
		subprocess.run(['sudo', 'ln', '-sfn', f'{Commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/error{state}.wav', f'{Commons.rootDir()}/assistant/custom_dialogue/sound/error.wav'])
