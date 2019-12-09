from collections import deque
from typing import Deque, Dict

from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class ContextSensitive(AliceSkill):
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)

	def __init__(self):
		self._history: Deque = deque(list(), 10)
		self._sayHistory: Dict[str, Deque] = dict()
		super().__init__()


	@IntentHandler('DeleteThis', isProtected=True)
	def deleteThisIntent(self, session: DialogSession):
		for skill in self.SkillManager.activeSkills.values():
			try:
				if skill['instance'].onContextSensitiveDelete(session.sessionId):
					self.endSession(sessionId=session.sessionId)
					return
			except Exception:
				continue


	@IntentHandler('EditThis', isProtected=True)
	def editThisIntent(self, session: DialogSession):
		for skill in self.SkillManager.activeSkills.values():
			try:
				if skill['instance'].onContextSensitiveEdit(session.sessionId):
					self.endSession(sessionId=session.sessionId)
					return
			except:
				continue


	@IntentHandler('RepeatThis', isProtected=True)
	def repeatThisIntent(self, session: DialogSession):
		self.endDialog(session.sessionId, text=self.getLastChat(siteId=session.siteId))


	def addToMessageHistory(self, session: DialogSession) -> bool:
		if session.message.topic in self.supportedIntents or session.message.topic == self._INTENT_ANSWER_YES_OR_NO or 'intent' not in session.message.topic:
			return False

		try:
			customData = session.customData

			if 'speaker' not in customData:
				customData['speaker'] = session.user
				data = session.payload
				data['customData'] = customData
				session.payload = data

			self._history.append(session)
		except Exception as e:
			self.logError('Error adding to intent history: {e}')
		return True


	def lastMessage(self) -> str:
		return self._history[-1] if self._history else None


	def addChat(self, text: str, siteId: str):
		if siteId not in self._sayHistory:
			self._sayHistory[siteId] = deque(list(), 10)

		self._sayHistory[siteId].append(text)


	def getLastChat(self, siteId: str) -> str:
		return self._sayHistory[siteId][-1] if self._sayHistory.get(siteId) else self.randomTalk('nothing')
