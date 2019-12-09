from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler

from .libraries import mpdhelper

#>>> mpd.status()
#{'volume': '44', 'repeat': '0', 'random': '0', 'single': '0', 'consume': '0', 'playlist': '2', 'playlistlength': '13', 'mixrampdb': '0.000000', 'state': 'play', 'song': '3', 'songid': '4', 'time': '1:178', 'elapsed': '0.789', 'bitrate': '128', 'audio': '44100:24:2', 'nextsong': '4', 'nextsongid': '5'}

# TODO have all intents enabled and answer if new state is not possible
# e.g. "play some music" when already playing -> "music is already playing"
# false matches?

class MpdClient(AliceSkill):
	"""
	Author: glueckself
	Description: Control an MPD server
	"""

	def __init__(self):
		#TODO volume, playlists, ...
		#TODO pause music if alice starts a dialogue

		super().__init__()

		self._host = self.getConfig('mpdHost')
		self._port = self.getConfig('mpdPort')
		self._password = self.getConfig('mpdPassword')

		self._mpdConnected = False
		self._mpd = mpdhelper.MPDClient()

		self._playbackStatus = None

		if not self._host:
			self.logWarning('MPD host not configured, not doing anything.')
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

		#self.logInfo(f'Music playing is now {self._playbackStatus}')


	def _connect(self):
		self._mpd.connect(self._host, self._port)
		if self._password:
			self._mpd.password(self._password)


	@IntentHandler('mpdPlay')
	def playIntent(self, session: DialogSession):
		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
		elif self._playbackStatus:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('alreadyPlaying'))
		else:
			self._mpd.play()
			self.endSession(sessionId=session.sessionId)


	@IntentHandler('mpdStop')
	def stopIntent(self, session: DialogSession):
		# note that _playbackStatus can also be None when disconnected.
		# while it shouldn't reach this line in that case, better to be on the safe side
		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
		elif not self._playbackStatus:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('alreadyStopped'))
		else:
			self._mpd.stop()
			self.endSession(sessionId=session.sessionId)


	@IntentHandler('mpdNext')
	def nextIntent(self, session: DialogSession):
		# TODO maybe say the title here if not playing
		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
		else:
			self._mpd.next()
			self.endSession(sessionId=session.sessionId)


	@IntentHandler('mpdPrev')
	def prevIntent(self, session: DialogSession):
		# TODO maybe say the title here if not playing
		if not self._mpdConnected:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('notConnected'))
		else:
			self._mpd.previous()
			self.endSession(sessionId=session.sessionId)
