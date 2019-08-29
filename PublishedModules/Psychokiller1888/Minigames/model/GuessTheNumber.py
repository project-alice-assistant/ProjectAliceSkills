# -*- coding: utf-8 -*-
import time

import os

import random

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class GuessTheNumber(MiniGame):

	_INTENT_PLAY_GAME = Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_NUMBER = Intent('AnswerNumber', isProtected=True)

	def __init__(self):
		super().__init__()
		self._number = 0
		self._start = 0


	@property
	def intents(self) -> list:
		return [
			self._INTENT_ANSWER_NUMBER
		]


	def start(self, session: DialogSession):
		super().start(session)

		redQueen = managers.ModuleManager.getModuleInstance('RedQueen')
		redQueen.changeRedQueenStat('happiness', 10)

		self._number = random.randint(1, 10000)

		self._start = time.time() - 4

		managers.MqttServer.continueDialog(
			sessionId=session.sessionId,
			text=managers.TalkManager.randomTalk(talk='guessTheNumberStart', module='Minigames'),
			intentFilter=[self._INTENT_ANSWER_NUMBER],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_NUMBER:
			if int(session.slotValue('Number')) == self._number:

				score = round(time.time() - self._start)
				m, s = divmod(score, 60)
				scoreFormatted = managers.LanguageManager.getTranslations(module='Minigames', key='minutesAndSeconds')[0].format(round(m), round(s))

				managers.MqttServer.playSound(
					soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'applause'),
					siteId=session.siteId,
					absolutePath=True
				)

				managers.MqttServer.endTalk(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk('guessTheNumberCorrect', 'Minigames').format(self._number, self._number)
				)

				if session.user != 'unknown' and managers.ModuleManager.getModuleInstance('Minigames').checkAndStoreScore(user=session.user, score=score, biggerIsBetter=False):
					managers.MqttServer.say(
						client=session.siteId,
						text=managers.TalkManager.randomTalk('guessTheNumberNewHighscore', 'Minigames').format(scoreFormatted),
						canBeEnqueued=True
					)
				else:
					managers.MqttServer.say(
						client=session.siteId,
						text=managers.TalkManager.randomTalk('guessTheNumberScore', 'Minigames').format(scoreFormatted),
						canBeEnqueued=True
					)

				managers.MqttServer.ask(
					text=managers.TalkManager.randomTalk('playAgain', 'Minigames'),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_PLAY_GAME,
					customData={
						'speaker': session.user,
						'askRetry': True
					}
				)

			elif int(session.slotValue('Number')) < self._number:
				managers.MqttServer.continueDialog(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk('guessTheNumberMore', 'Minigames'),
					intentFilter=[self._INTENT_ANSWER_NUMBER],
					previousIntent=self._INTENT_PLAY_GAME
				)

			else:
				managers.MqttServer.continueDialog(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk('guessTheNumberLess', 'Minigames'),
					intentFilter=[self._INTENT_ANSWER_NUMBER],
					previousIntent=self._INTENT_PLAY_GAME
				)
