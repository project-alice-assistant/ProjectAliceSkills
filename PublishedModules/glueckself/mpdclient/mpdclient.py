import mpdhelper

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.commons import online

class mpdclient(Module):
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
		
		config = self.getConfig('mpdClient')
		self._host = config.get('mpdHost')
		self._port = config.get('mpdPort')
		self._password = config.get('mpdPassword')
		
		self._mpdConnected = False
		
		if self._host:
			self._connect()
		else:
			self._logger.warn(f'[{self.name}] MPD host not configured, not doing anything.')
		
	def _connect(self):
		self._mpd = mpdhelper.MPDClient()
		try:
			self._mpd.connect(self._host, self._port, 5)
		except:
			self._logger.warn(f'[{self.name}] Failed to connect to mpd host {self._host}:{self._port}, retrying in 10s.')
			self.ThreadManager.doLater(interval=10, func=self._connect)
			return
		
		if self._password:
			self._mpd.password(self._password)
			
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
