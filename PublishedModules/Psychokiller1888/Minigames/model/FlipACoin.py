# -*- coding: utf-8 -*-
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
			rnd = random.randint(1, 100)

			coin = 'heads'
			if rnd % 2 == 0:
				coin = 'tails'

			managers.MqttServer.playSound(
				soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'coinflip'),
				sessionId='coinflip',
				siteId=session.siteId,
				absolutePath=True
			)

			self._started = False

			if session.slotValue('HeadsOrTails') == coin:
				managers.MqttServer.continueDialog(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk(talk='flipACoinUserWins', module='Minigames').format(session.slots['HeadsOrTails']),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_PLAY_GAME
				)
			else:
				managers.MqttServer.continueDialog(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk(
						talk='flipACoinUserLooses',
						module='Minigames'
					).format(managers.LanguageManager.getTranslations(module='Minigames', key=coin, toLang=managers.LanguageManager.activeLanguage)[0]),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_PLAY_GAME,
					customData={
						'askRetry': True
					}
				)
