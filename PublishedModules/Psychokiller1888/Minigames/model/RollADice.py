import os

import random

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.commons import commons
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

		managers.MqttServer.playSound(
			soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'rollADice'),
			sessionId='rollADice',
			siteId=session.siteId,
			absolutePath=True
		)

		redQueen = managers.ModuleManager.getModuleInstance('RedQueen')
		redQueen.changeRedQueenStat('happiness', 5)

		managers.MqttServer.endTalk(
			sessionId=session.sessionId,
			text=managers.TalkManager.randomTalk(
				talk='rollADiceResult',
				module='Minigames'
			).format(random.randint(1, 6))
		)


	def onMessage(self, intent: str, session: DialogSession):
		pass
