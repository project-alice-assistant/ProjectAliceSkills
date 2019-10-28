import subprocess
import time
from pathlib import Path

import tempfile

from core.ProjectAliceExceptions import ModuleStartDelayed
from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.interface.views.AdminAuth import AdminAuth
from core.util.Decorators import Decorators
from core.commons import constants
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
			(self._INTENT_GLOBAL_STOP, self.globalStopIntent),
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
			'addingPinCode': self.addUserPinCode,
			'userAuth': self.authUser
		}

		self._threads = dict()
		super().__init__(self._INTENTS, authOnlyIntents=self._AUTH_ONLY_INTENTS)


	def authUser(self, session: DialogSession, **_kwargs):
		if 'Number' not in session.slotsAsObjects:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', module='system'),
				intentFilter=[self._INTENT_ANSWER_NUMBER],
				currentDialogState='userAuth'
			)
			return

		pin = ''.join([str(int(x.value['value'])) for x in session.slotsAsObjects['Number']])

		user = self.UserManager.getUser(session.customData['user'])
		if not user:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('userAuthUnknown')
			)

		if not user.checkPassword(pin):
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('authFailed')
			)
		else:
			self.UserManager.getUser(session.user).isAuthenticated = True
			AdminAuth.loginUser()
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('authOk')
			)

		self.ThreadManager.getEvent('authUser').clear()


	def addNewUser(self, session: DialogSession, **_kwargs):
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('addUserWhatsTheName'),
			intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
			currentDialogState='addingUser'
		)


	def askCreateWakeword(self, session: DialogSession, **_kwargs):
		if 'pinCode' in session.customData:
			if self.Commons.isYes(session):
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
		
		pin = ''.join([str(int(x.value['value'])) for x in session.slotsAsObjects['Number']])

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
				if self.delayed: # type: ignore
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
		if self.Commons.isYes(session):
			self.WakewordManager.tryCaptureFix()
			self.confirmWakewordTrimming(intent=intent, session=session)
			return
		
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
				return
			time.sleep(0.5)

		filepath = Path(tempfile.gettempdir(), str(self.WakewordManager.getLastSampleNumber())).with_suffix('.wav')

		if not filepath.exists():
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('wakewordCaptureFailed'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState='confirmingRecaptureAfterFailure'
			)
			return
		
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
		if self.Commons.isYes(session):
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
		if not self.Commons.isYes(session):
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('soWhatsTheName'),
				intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
				currentDialogState='addingUser'
			)
			return
		
		if session.customData['username'] in self.UserManager.getAllUserNames(skipGuests=False):
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='userAlreadyExist', replace=[session.slots['Name']]),
				intentFilter=[self._INTENT_ANSWER_NAME, self._INTENT_SPELL_WORD],
				currentDialogState='addingUser'
			)
			return

		accessLevel = session.slots.get('UserAccessLevel', session.customData.get('UserAccessLevel'))
		if not accessLevel:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('addUserWhatAccessLevel'),
				intentFilter=[self._INTENT_ANSWER_ACCESSLEVEL],
				currentDialogState='confirmingUsername',
				slot='UserAccessLevel'
			)
			return

		text = 'addAdminPin' if accessLevel.lower() == AccessLevel.ADMIN.name.lower() else 'addUserPin'

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text),
			intentFilter=[self._INTENT_ANSWER_NUMBER],
			currentDialogState='addingPinCode',
			customData={
				'accessLevel': accessLevel
			}
		)


	def confirmUsername(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_NAME:
			username = str(session.slots['Name']).lower()
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
		duration = self.Commons.getDuration(session)
		if duration:
			self.ThreadManager.doLater(interval=duration, func=self.unmuteSite, args=[session.siteId])

		aliceModule = self.ModuleManager.getModuleInstance('AliceSatellite')
		if aliceModule:
			aliceModule.notifyDevice('projectalice/devices/stopListen', siteId=session.siteId)

		self.endDialog(sessionId=session.sessionId)


	def addDeviceIntent(self, session: DialogSession, **_kwargs):
		if self.DeviceManager.isBusy():
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
			return

		hardware = session.slots.get('Hardware')
		espType = session.slots.get('EspType')
		room = session.slots.get('Room')
		if not hardware:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatHardware'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				currentDialogState='specifyingHardware'
			)
			return

		if hardware == 'esp' and not espType:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatESP'),
				intentFilter=[self._INTENT_ANSWER_HARDWARE_TYPE, self._INTENT_ANSWER_ESP_TYPE],
				currentDialogState='specifyingEspType'
			)
			return

		if not room:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whichRoom'),
				intentFilter=[self._INTENT_ANSWER_ROOM],
				currentDialogState='specifyingRoom'
			)
			return

		if hardware == 'esp':
			if not self.ModuleManager.isModuleActive('Tasmota'):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('requireTasmotaModule'))

			elif self.DeviceManager.isBusy():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))

			elif not self.DeviceManager.startTasmotaFlashingProcess(self.Commons.cleanRoomNameToSiteId(room), espType, session):
				self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('espFailed'), session.siteId])

		elif hardware == 'zigbee':
			if not self.ModuleManager.isModuleActive('Zigbee2Mqtt'):
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('requireZigbeeModule'))
				return

			if self.DeviceManager.isBusy():
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('busy'))
				return

			self.DeviceManager.addZigBeeDevice()

		elif hardware == 'satellite':
			if self.DeviceManager.startBroadcastingForNewDevice(self.Commons.cleanRoomNameToSiteId(room), session.siteId):
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
		if self.Commons.isYes(session):
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('askRebootModules'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState='confirmingModuleReboot'
			)
		else:
			self.endDialog(session.sessionId, self.randomTalk('abortReboot'))


	def reboot(self, session: DialogSession, **_kwargs):
		value = 'greetAndRebootModules' if self.Commons.isYes(session) else 'greet'

		self.ConfigManager.updateAliceConfiguration('onReboot', value)
		self.endDialog(session.sessionId, self.randomTalk('confirmRebooting'))
		self.ThreadManager.doLater(interval=5, func=subprocess.run, args=[['sudo', 'shutdown', '-r', 'now']])


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


	def onStart(self) -> dict:
		super().onStart()
		self.changeFeedbackSound(inDialog=False)

		if not self.UserManager.users:
			if not self.delayed:
				self.logWarning('No user found in database')
				raise ModuleStartDelayed(self.name)
			self._addFirstUser()

		return self.supportedIntents


	def onHotword(self, siteId: str, user: str = constants.UNKNOWN_USER):
		if self.ThreadManager.getEvent('authUserWaitWakeword').isSet():
			self.ThreadManager.getEvent('authUserWaitWakeword').clear()
			self.ThreadManager.newEvent('authUser').set()


	def onUserCancel(self, session: DialogSession):
		if self.delayed:
			self.delayed = False

			if not self.ThreadManager.getEvent('AddingWakeword').isSet():
				self.say(text=self.randomTalk('noStartWithoutAdmin'), siteId=session.siteId)
				self.ThreadManager.doLater(interval=10, func=self.stop)
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
		self.onSessionTimeout(session)


	def onSessionStarted(self, session: DialogSession):
		self.changeFeedbackSound(inDialog=True, siteId=session.siteId)

		if self.ThreadManager.getEvent('authUser').isSet() and session.currentState != 'userAuth':
			self.SnipsServicesManager.toggleFeedbackSound(state='on')

			user = self.UserManager.getUser(session.user)
			if user == constants.UNKNOWN_USER:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('userAuthUnknown')
				)
			elif self.UserManager.hasAccessLevel(session.user, AccessLevel.ADMIN):
				# End the session immediately because the ASR is listening to the previous wakeword call
				self.endSession(sessionId=session.sessionId)

				AdminAuth.user = user

				self.ask(
					text=self.randomTalk('greetAndNeedPinCode', replace=[session.user]),
					siteId=session.siteId,
					intentFilter=[self._INTENT_ANSWER_NUMBER],
					currentDialogState='userAuth',
					customData={
						'user': session.user.lower()
					}
				)
			else:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('userAuthAccessLevelTooLow')
				)


	def onSessionEnded(self, session: DialogSession):
		if not self.ThreadManager.getEvent('AddingWakeword').isSet():
			self.changeFeedbackSound(inDialog=False, siteId=session.siteId)
			self.onSessionTimeout(session)


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


	def deviceGreetingIntent(self, session: DialogSession, **_kwargs):
		uid = session.payload.get('uid')
		siteId = session.payload.get('siteId')
		if not uid or not siteId:
			self.logWarning('A device tried to connect but is missing informations in the payload, refused')
			self.publish(topic='projectalice/devices/connectionRefused', payload={'siteId': siteId})
			return

		device = self.DeviceManager.deviceConnecting(uid=uid)
		if device:
			self.logInfo(f'Device with uid {device.uid} of type {device.deviceType} in room {device.room} connected')
			self.publish(topic='projectalice/devices/connectionAccepted', payload={'siteId': siteId, 'uid': uid})
		else:
			self.publish(topic='projectalice/devices/connectionRefused', payload={'siteId': siteId, 'uid': uid})


	@Decorators.online(text='noAssistantUpdateOffline')
	def aliceUpdateIntent(self, session: DialogSession, **_kwargs):
		self.publish('hermes/leds/systemUpdate')
		updateTypes = {
			'all': 1,
			'alice': 2,
			'assistant': 3,
			'modules': 4
		}
		update = updateTypes.get(session.slots.get('WhatToUpdate', 'all'), 5)

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmAssistantUpdate'))
		if update in {1, 5}:  # All or system
			self.logInfo('Updating system')
			self.ThreadManager.doLater(interval=2, func=self.systemUpdate)

		if update in {1, 4}:  # All or modules
			self.logInfo('Updating modules')
			self.ModuleManager.checkForModuleUpdates()

		if update in {1, 2}:  # All or Alice
			self.logInfo('Updating Alice')

		if update in {1, 3}:  # All or Assistant
			self.logInfo('Updating assistant')

			if not self.LanguageManager.activeSnipsProjectId:
				self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('noProjectIdSet'), session.siteId])
			elif not self.SnipsConsoleManager.loginCredentialsAreConfigured():
				self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('bundleUpdateNoCredentials'), session.siteId])
			else:
				self.ThreadManager.doLater(interval=2, func=self.SamkillaManager.sync)


	def globalStopIntent(self, session: DialogSession, **_kwargs):
		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('confirmGlobalStop'))


	def unmuteSite(self, siteId):
		self.ModuleManager.getModuleInstance('AliceSatellite').notifyDevice('projectalice/devices/startListen', siteId=siteId)
		self.ThreadManager.doLater(interval=1, func=self.say, args=[self.randomTalk('listeningAgain'), siteId])


	@staticmethod
	def restart():
		subprocess.run(['sudo', 'systemctl', 'restart', 'ProjectAlice'])


	@staticmethod
	def stop():
		subprocess.run(['sudo', 'systemctl', 'stop', 'ProjectAlice'])


	@classmethod
	def systemUpdate(cls):
		subprocess.run(['sudo', 'apt-get', 'update'])
		subprocess.run(['sudo', 'apt-get', 'dist-upgrade', '-y'])
		subprocess.run(['git', 'stash'])
		subprocess.run(['git', 'pull'])
		subprocess.run(['git', 'stash', 'clear'])
		SuperManager.getInstance().threadManager.doLater(interval=2, func=cls.restart)


	def cancelUnregister(self):
		thread = self._threads.pop('unregisterTimeout', None)
		if thread:
			thread.cancel()


	def langSwitch(self, newLang: str, siteId: str):
		self.publish(topic='hermes/asr/textCaptured', payload={'siteId': siteId})
		subprocess.run([f'{self.Commons.rootDir()}/system/scripts/langSwitch.sh', newLang])
		self.ThreadManager.doLater(interval=3, func=self._confirmLangSwitch, args=[siteId])


	def _confirmLangSwitch(self, siteId: str):
		self.publish(topic='hermes/leds/onStop', payload={'siteId': siteId})
		self.say(text=self.randomTalk('langSwitch'), siteId=siteId)


	# noinspection PyUnusedLocal
	def changeFeedbackSound(self, inDialog: bool, siteId: str = 'all'):
		if not Path(self.Commons.rootDir(), 'assistant').exists():
			return

		# Unfortunately we can't yet get rid of the feedback sound because Alice hears herself finishing the sentence and capturing part of it
		state = '_ask' if inDialog else ''

		subprocess.run(['sudo', 'ln', '-sfn', f'{self.Commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/start_of_input{state}.wav', f'{self.Commons.rootDir()}/assistant/custom_dialogue/sound/start_of_input.wav'])
		subprocess.run(['sudo', 'ln', '-sfn', f'{self.Commons.rootDir()}/system/sounds/{self.LanguageManager.activeLanguage}/error{state}.wav', f'{self.Commons.rootDir()}/assistant/custom_dialogue/sound/error.wav'])


	def explainInterfaceAuth(self):
		self.ThreadManager.getEvent('authUser').clear()
		self.ThreadManager.newEvent('authUserWaitWakeword').set()
		self.SnipsServicesManager.toggleFeedbackSound(state='off')
		self.say(
			text=self.randomTalk('explainInterfaceAuth'),
			siteId=constants.ALL
		)
