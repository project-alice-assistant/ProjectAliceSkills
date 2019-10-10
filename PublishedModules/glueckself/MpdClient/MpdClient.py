from modules.MpdClient import mpdhelper

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession

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

		self._playbackStatus = None
		
		if not self._host:
			self._logger.warn(f'[{self.name}] MPD host not configured, not doing anything.')
			return
		
		self.ThreadManager.doLater(interval=1, func=self._mpdPollStatus)

	def _mpdPollStatus(self):
		status = self._mpd.status()
		self._mpdProcessStatus(status)
		self.ThreadManager.doLater(interval=1, func=self._mpdPollStatus)

	def _mpdProcessStatus(self, status: dict):
		if not status:
			self._mpdConnected = False
			self._playbackStatus = None
			self._mpd.disconnect()
			self._connect()
			return

		self._mpdConnected = True
		self._playbackStatus = (status['state'] == 'play')

		#self._logger.info(f'[{self.name}] Music playing is now {self._playbackStatus}')

	def _connect(self):
		self._mpd.connect(self._host, self._port)
		if self._password:
			self._mpd.password(self._password)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
			return True

		if intent == self._INTENT_PLAY:
			if self._playbackStatus:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('alreadyPlaying'))
			else:
				self._mpd.play()
				self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_STOP:
			# note that _playbackStatus can also be None when disconnected.
			# while it shouldn't reach this line in that case, better to be on the safe side
			if not self._playbackStatus:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk('alreadyStopped'))
			else:
				self._mpd.stop()
				self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_NEXT:
			# TODO maybe say the title here if not playing
			self._mpd.next()
			self.endDialog(sessionId=session.sessionId)
			return True
		elif intent == self._INTENT_PREV:
			# TODO maybe say the title here if not playing
			self._mpd.previous()
			self.endDialog(sessionId=session.sessionId)
			return True
		else:
			return False
		#TODO volume, playlists, ...
		#TODO pause music if alice starts a dialogue
