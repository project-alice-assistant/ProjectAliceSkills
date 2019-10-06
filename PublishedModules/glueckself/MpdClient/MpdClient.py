import mpdhelper

from core.ProjectAliceExceptions import ModuleStartDelayed, ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.commons import online

#>>> mpd.status()
#{'volume': '44', 'repeat': '0', 'random': '0', 'single': '0', 'consume': '0', 'playlist': '2', 'playlistlength': '13', 'mixrampdb': '0.000000', 'state': 'play', 'song': '3', 'songid': '4', 'time': '1:178', 'elapsed': '0.789', 'bitrate': '128', 'audio': '44100:24:2', 'nextsong': '4', 'nextsongid': '5'}

# TODO have all intents enabled and answer if new state is not possible
# e.g. "play some music" when already playing -> "music is already playing"
# false matches?

class MpdClient(Module):
	"""
	Author: glueckself
	Description: Control an MPD server
	"""

	_INTENT_PLAY = Intent('mpdPlay')
	_INTENT_STOP = Intent('mpdStop')
	_INTENT_NEXT = Intent('mpdNext')
	_INTENT_PREV = Intent('mpdPrev')

	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_PLAY,
			self._INTENT_STOP,
			self._INTENT_NEXT,
			self._INTENT_PREV
		]

		super().__init__(self._SUPPORTED_INTENTS)
		
		self._host = self.getConfig('mpdHost')
		self._port = self.getConfig('mpdPort')
		self._password = self.getConfig('mpdPassword')
		
		self._mpdConnected = False
		self._mpd = mpdhelper.MPDClient()
		
		if not self._host:
			self._logger.warn(f'[{self.name}] MPD host not configured, not doing anything.')
			return
		
		self._refreshTimer = self.ThreadManager.newTimer(interval=1, func=self._mpd_poll_status, args=self, autoStart=True)
	
	def _mpd_poll_status(self):
		status = self._mpd.status()
		self._mpd_process_status(status)
		self._refreshTimer.start()
		
	def _mpd_process_status(self, status: dict):
		if not status:
			self._mpd.disconnect()
			self._mpdConnected = False
			self._connect()
			return
		
		playbackStatus = False
		if status['state'] == 'play':
			playbackStatus = True
		
		try:
			intents = list()
			# when playing: stop, next, prev. when stopped: play
			intents = [
				{'intentId': 'mpdPlay', 'enable': not playbackStatus },
				{'intentId': 'mpdStop', 'enable': playbackStatus },
				{'intentId': 'mpdNext', 'enable': playbackStatus },
				{'intentId': 'mpdPrev', 'enable': playbackStatus }
			]
			self.MqttManager.configureIntents(intents)
		except Exception as e:
			self._logger.warning(f'[{self.name}] Failed to update intents to match the mpd state: {e}')
	
	def _connect(self):
		if not self._mpd.connect(self._host, self._port):
			self._logger.warn(f'[{self.name}] Failed to connect to mpd host {self._host}:{self._port}, retrying in 10s.')
			return
		
		if self._password:
			if not self._mpd.password(self._password):
				# handle invalid password
				pass
			
		self._logger.info(f'[{self.name}] Connected to mpd host {self._host}:{self._port}')
		self._mpdConnected = True
		
	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False
		
		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
			return True

		if intent == self._INTENT_PLAY:
			self._mpd.play()
			self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_STOP:
			self._mpd.stop()
			self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_NEXT:
			self._mpd.next()
			self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_PREV:
			self._mpd.prev()
			self.endDialog(sessionId=session.sessionId)
			return True
		else:
			return False
