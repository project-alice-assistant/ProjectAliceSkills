import json
from typing import Dict, Deque
from collections import deque

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class ContextSensitive(Module):
	_INTENT_DELETE_THIS = Intent('DeleteThis', isProtected=True)
	_INTENT_REPEAT_THIS = Intent('RepeatThis', isProtected=True)
	_INTENT_EDIT_THIS = Intent('EditThis', isProtected=True)
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)


	def __init__(self):
		self._INTENTS = {
			self._INTENT_DELETE_THIS: self.deleteThisIntent,
			self._INTENT_REPEAT_THIS: self.repeatThisIntent,
			self._INTENT_EDIT_THIS: self.editThisIntent
		}

		self._history: Deque = deque(list(), 10)
		self._sayHistory: Dict[str, Deque] = dict()

		super().__init__(self._INTENTS)


	def deleteThisIntent(self, intent: str, session: DialogSession) -> bool:
		modules = self.ModuleManager.getModules()
		for module in modules.values():
			try:
				if module['instance'].onContextSensitiveDelete(session.sessionId):
					self.endSession(sessionId=session.sessionId)
					return True
			except Exception:
				continue
		return True


	def editThisIntent(self, intent: str, session: DialogSession) -> bool:
		modules = self.ModuleManager.getModules()
		for module in modules.values():
			try:
				if module['instance'].onContextSensitiveEdit(session.sessionId):
					self.MqttManager.endDialog(sessionId=session.sessionId)
					return True
			except:
				continue
		return True

	def repeatThisIntent(self, intent: str, session: DialogSession) -> bool:
		self.endDialog(session.sessionId, text=self.getLastChat(siteId=session.siteId))
		return True


	def addToMessageHistory(self, session: DialogSession) -> bool:
		if session.message.topic in self._INTENTS or session.message.topic == self._INTENT_ANSWER_YES_OR_NO or 'intent' not in session.message.topic:
			return False

		try:
			customData = session.customData

			if 'speaker' not in customData:
				customData['speaker'] = session.user
				data = session.payload
				data['customData'] = customData
				session.payload = data

			self._history.appendleft(session)
		except Exception as e:
			self.logError('Error adding to intent history: {e}')
		return True


	def lastMessage(self):
		return self._history[-1] if self._history else None


	def addChat(self, text: str, siteId: str):
		if siteId not in self._sayHistory:
			self._sayHistory[siteId] = deque(list(), 10)

		self._sayHistory[siteId].appendleft(text)


	def getLastChat(self, siteId: str):
		return self._sayHistory[siteId][-1] if self._sayHistory.get(siteId) else self.randomTalk('nothing')
