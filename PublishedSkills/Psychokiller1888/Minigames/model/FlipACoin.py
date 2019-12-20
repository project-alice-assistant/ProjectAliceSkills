import random

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class FlipACoin(MiniGame):

	_INTENT_ANSWER_HEADS_OR_TAIL = Intent('AnswerHeadsOrTail', isProtected=True)

	def __init__(self):
		super().__init__()
		self._intents = [
			self._INTENT_ANSWER_HEADS_OR_TAIL
		]


	def start(self, session: DialogSession):
		super().start(session)

		self.MqttManager.continueDialog(
			sessionId=session.sessionId,
			text=self.TalkManager.randomTalk(talk='flipACoinStart', skill='Minigames'),
			intentFilter=[self._INTENT_ANSWER_HEADS_OR_TAIL],
			currentDialogState=self.PLAYING_MINIGAME_STATE
		)


	def onMessage(self, session: DialogSession):
		if session.intentName == self._INTENT_ANSWER_HEADS_OR_TAIL:
			coin = random.choice(['heads', 'tails'])

			self.sound('coinflip', session.siteId)

			redQueen = SuperManager.getInstance().skillManager.getSkillInstance('RedQueen')
			redQueen.changeRedQueenStat('happiness', 5)

			if session.slotValue('HeadsOrTails') == coin:
				result = 'flipACoinUserWins'
				redQueen.changeRedQueenStat('frustration', 1)
			else:
				result = 'flipACoinUserLooses'
				redQueen.changeRedQueenStat('frustration', -5)
				redQueen.changeRedQueenStat('happiness', 5)

			self.MqttManager.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk(
					talk=result,
					skill='Minigames'
				).format(self.LanguageManager.getTranslations(skill='Minigames', key=coin)[0]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState=self.ANSWERING_PLAY_AGAIN_STATE
			)
