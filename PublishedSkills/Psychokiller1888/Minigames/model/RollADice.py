import random

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class RollADice(MiniGame):

	_INTENT_PLAY_GAME = Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)

	def __init__(self):
		super().__init__()


	@property
	def intents(self) -> list:
		return list()


	def start(self, session: DialogSession):
		super().start(session)

		self.sound('rollADice', session.siteId)

		redQueen = SuperManager.getInstance().skillManager.getSkillInstance('RedQueen')
		redQueen.changeRedQueenStat('happiness', 5)

		SuperManager.getInstance().mqttManager.endDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(
				talk='rollADiceResult',
				skill='Minigames'
			).format(random.randint(1, 6))
		)
