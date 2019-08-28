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
	_INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS = Intent('AnswerRockPaperOrScissors', isProtected=True)

	def __init__(self):
		super().__init__()


	@property
	def intents(self) -> list:
		return [
			self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS
		]


	def start(self, session: DialogSession):
		super().start(session)

		managers.MqttServer.continueDialog(
			sessionId=session.sessionId,
			text=managers.TalkManager.randomTalk(talk='rockPaperScissorsStart', module='Minigames'),
			intentFilter=[self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, intent: str, session: DialogSession):
		if intent == self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS:
			rnd = random.randint(1, 100)

			if rnd < 33:
				me = 'rock'
			elif 33 <= rnd < 66:
				me = 'paper'
			else:
				me = 'scissors'

			managers.MqttServer.playSound(
				soundFile=os.path.join(commons.rootDir(), 'modules', 'Minigames', 'sounds', 'drum_suspens'),
				sessionId='rockpaperscissors',
				siteId=session.siteId,
				absolutePath=True
			)


			if session.slotValue('RockPaperOrScissors') == me:
				managers.MqttServer.continueDialog(
					sessionId=session.sessionId,
					text=managers.TalkManager.randomTalk(talk='rockPaperScissorsTie', module='Minigames').format(session.slotValue('RockPaperOrScissors')),
					intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
					previousIntent=self._INTENT_PLAY_GAME,
					customData={
						'askRetry': True
					}
				)
			else:
				player = session.slotValue('RockPaperOrScissors')

				# Player wins
				if player == 'rock' and me == 'scissors' or player == 'paper' and me == 'rock' or player == 'scissors' and me == 'paper':
					managers.MqttServer.continueDialog(
						sessionId=session.sessionId,
						text=managers.TalkManager.randomTalk(
							talk='rockPaperScissorsWins',
							module='Minigames'
						).format(managers.LanguageManager.getTranslations(module='Minigames', key=me, toLang=managers.LanguageManager.activeLanguage)[0]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_PLAY_GAME,
						customData={
							'askRetry': True
						}
					)
				else:
					managers.MqttServer.continueDialog(
						sessionId=session.sessionId,
						text=managers.TalkManager.randomTalk(
							talk='rockPaperScissorsLooses',
							module='Minigames'
						).format(managers.LanguageManager.getTranslations(module='Minigames', key=me, toLang=managers.LanguageManager.activeLanguage)[0]),
						intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
						previousIntent=self._INTENT_PLAY_GAME,
						customData={
							'askRetry': True
						}
					)
