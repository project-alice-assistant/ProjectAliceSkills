# -*- coding: utf-8 -*-
import time

import os

import random

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class FlipACoin(MiniGame):

	_INTENT_PLAY_GAME = Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_HEADS_OR_TAIL = Intent('AnswerHeadsOrTail', isProtected=True)

	def __init__(self):
		super().__init__()


	@property
	def intents(self) -> list:
		return [
			self._INTENT_ANSWER_HEADS_OR_TAIL
		]


	def start(self, session: DialogSession):
		super().start(session)

		managers.MqttServer.continueDialog(
			sessionId=session.sessionId,
			text=managers.TalkManager.randomTalk(talk='flipACoinStart', module='Minigames'),
			intentFilter=[self._INTENT_ANSWER_HEADS_OR_TAIL],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_HEADS_OR_TAIL:
			coin = random.choice(['heads', 'tails'])

			managers.MqttServer.playSound(
				soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'coinflip'),
				sessionId='coinflip',
				siteId=session.siteId,
				absolutePath=True
			)

			redQueen = managers.ModuleManager.getModuleInstance('RedQueen')
			redQueen.changeRedQueenStat('happiness', 5)

			if session.slotValue('HeadsOrTails') == coin:
				result = 'flipACoinUserWins'
				redQueen.changeRedQueenStat('frustration', 1)
			else:
				result = 'flipACoinUserLooses'
				redQueen.changeRedQueenStat('frustration', -5)
				redQueen.changeRedQueenStat('hapiness', 5)

			managers.MqttServer.continueDialog(
				sessionId=session.sessionId,
				text=managers.TalkManager.randomTalk(
					talk=result,
					module='Minigames'
				).format(managers.LanguageManager.getTranslations(module='Minigames', key=coin, toLang=managers.LanguageManager.activeLanguage)[0]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_PLAY_GAME,
				customData={
					'askRetry': True
				}
			)
