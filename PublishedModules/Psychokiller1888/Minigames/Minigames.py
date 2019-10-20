import importlib
from typing import Optional

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from .model import MiniGame


class Minigames(Module):
	"""
	Author: Psychokiller1888
	Description: Play a collection of many little games with alice
	"""

	_INTENT_PLAY_GAME 			= Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO 	= Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_MINI_GAME 	= Intent('AnswerMiniGame', isProtected=True)

	_SUPPORTED_GAMES 			= [
		'FlipACoin',
		'RockPaperScissors',
		'RollADice',
		'GuessTheNumber'
	]

	DATABASE = {
		'highscores': [
			'username TEXT NOT NULL',
			'score INTEGER NOT NULL',
			'timestamp INTEGER NOT NULL'
		]
	}

	def __init__(self):
		self._INTENTS = [
			(self._INTENT_PLAY_GAME, self.playGameIntent),
			(self._INTENT_ANSWER_MINI_GAME, self.playGameIntent),
			(self._INTENT_ANSWER_YES_OR_NO, self.answerAnotherGame)
		]

		self._minigames = dict()
		self._minigame: MiniGame = None

		for game in self._SUPPORTED_GAMES:
			try:
				lib = importlib.import_module(f'modules.Minigames.model.{game}')
				klass = getattr(lib, game)
				minigame = klass()

				self._minigames[game] = minigame

				minigameIntentList = list()
				for intent in minigame.intents:
					minigameIntentList.append((intent, self.minigameIntent))

				self._INTENTS = [*self._INTENTS, *minigameIntentList]
			except Exception as e:
				self.logError(f'Something went wrong loading the minigame "{game}": {e}')

		super().__init__(self._INTENTS, databaseSchema=self.DATABASE)


	def onSessionTimeout(self, session: DialogSession):
		if self._minigame:
			self._minigame.started = False


	def onUserCancel(self, session: DialogSession):
		if self._minigame:
			self._minigame.started = False


	def minigameIntent(self, session: DialogSession, intent: str) -> Optional[bool]:
		if session.currentState != MiniGame.MiniGame.PLAYING_MINIGAME_STATE:
			return False

		self._minigame.onMessage(intent, session)


	def answerAnotherGame(self, session: DialogSession, **_kwargs):
		if not self.Commons.isYes(session):
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('endPlaying')
			)
		else:
			if session.currentState != MiniGame.MiniGame.ANSWERING_PLAY_AGAIN_STATE:
				self.continueDialog(
					sessionId=session.sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME],
					text=self.TalkManager.randomTalk('whichGame')
				)
			else:
				self._minigame.start()
		return


	def playGameIntent(self, intent: str, session: DialogSession) -> bool:
		sessionId = session.sessionId
		slots = session.slots

		if not self._minigame or not self._minigame.started:
			if 'WhichGame' not in slots:
				self.continueDialog(
					sessionId=sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME],
					text=self.TalkManager.randomTalk('whichGame')
				)

			elif session.slotValue('WhichGame') not in self._SUPPORTED_GAMES:
				self.continueDialog(
					sessionId=sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME, self._INTENT_ANSWER_YES_OR_NO],
					text=self.TalkManager.randomTalk('unknownGame'),
					currentDialogState='answeringPlayAnotherGamer'
				)

			else:
				game = session.slotValue('WhichGame')
				self._minigame = self._minigames[game]
				self._minigame.start(session)

		elif self._minigame is not None:
			self._minigame.onMessage(intent, session)
		return True
