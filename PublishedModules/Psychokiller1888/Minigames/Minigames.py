# -*- coding: utf-8 -*-

import importlib

import core.base.Managers as managers
from core.commons import commons
from .model import MiniGame
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Minigames(Module):
	"""
	Author: Psychokiller1888
	Description: Play a collection of many little games with alice
	"""

	_INTENT_PLAY_GAME 			= Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO 	= Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_MINI_GAME 	= Intent('AnswerMiniGame', isProtected=True)

	_SUPPORTED_GAMES 			= [
		'FlipACoin'
	]

	DATABASE = {
		'highscores': [
			'username UNIQUE TEXT NOT NULL',
			'score INTEGER NOT NULL',
			'timestamp INTEGER NOT NULL'
		]
	}

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_PLAY_GAME,
			self._INTENT_ANSWER_MINI_GAME,
			self._INTENT_ANSWER_YES_OR_NO
		]

		super().__init__(self._SUPPORTED_INTENTS)

		self._minigames = dict()
		self._minigame: MiniGame = None

		for game in self._SUPPORTED_GAMES:
			try:
				lib = importlib.import_module('modules.Minigames.model.{}'.format(game))
				klass = getattr(lib, game)
				minigame = klass()
				self._minigames[game] = minigame
				self._SUPPORTED_INTENTS += minigame.intents
			except Exception as e:
				self._logger.error('[{}] Something went wrong loading the minigame "{}": {}'.format(self.name, game, e))


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		slots = session.slots

		if not self._minigame or not self._minigame.started:
			if intent == self._INTENT_PLAY_GAME or (intent == self._INTENT_ANSWER_MINI_GAME and session.previousIntent == self._INTENT_PLAY_GAME):
				if 'WhichGame' not in slots.keys():
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						intentFilter=[self._INTENT_ANSWER_MINI_GAME],
						text=managers.TalkManager.randomTalk('whichGame'),
						previousIntent=self._INTENT_PLAY_GAME
					)

				elif session.slotValue('WhichGame') not in self._SUPPORTED_GAMES:
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						intentFilter=[self._INTENT_ANSWER_MINI_GAME, self._INTENT_ANSWER_YES_OR_NO],
						text=managers.TalkManager.randomTalk('unknownGame'),
						previousIntent=self._INTENT_PLAY_GAME
					)

				else:
					game = session.slotValue('WhichGame')

					self._minigame = self._minigames[game]
					self._minigame.start(session)

			elif intent == self._INTENT_ANSWER_YES_OR_NO:
				if not commons.isYes(session.message):
					managers.MqttServer.endTalk(
						sessionId=sessionId,
						text=self.randomTalk('endPlaying')
					)

		elif self._minigame is not None:
			if intent == self._INTENT_ANSWER_YES_OR_NO and session.customData and 'askRetry' in session.customData.keys():
				if commons.isYes(session.message):
					self._minigame.start(session)
				else:
					self._minigame = None
					managers.MqttServer.endTalk(
						sessionId=sessionId,
						text=self.randomTalk('endPlaying')
					)
			else:
				self._minigame.onMessage(intent, session)

		return True
