import os
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

		SuperManager.getInstance().mqttManager.playSound(
			soundFile=os.path.join(SuperManager.getInstance().commons.rootDir(), 'modules', 'Minigames', 'sounds', 'rollADice'),
			sessionId='rollADice',
			siteId=session.siteId,
			absolutePath=True
		)

		redQueen = SuperManager.getInstance().moduleManager.getModuleInstance('RedQueen')
		redQueen.changeRedQueenStat('happiness', 5)

		SuperManager.getInstance().mqttManager.endDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(
				talk='rollADiceResult',
				module='Minigames'
			).format(random.randint(1, 6))
		)


	def onMessage(self, intent: str, session: DialogSession):
		pass
