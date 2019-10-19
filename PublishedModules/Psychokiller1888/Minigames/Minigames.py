import importlib
import time

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons import Commons
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
		self._INTENTS	= {
			self._INTENT_PLAY_GAME: self.playGameIntent,
			self._INTENT_ANSWER_MINI_GAME: self.answerMinigameIntent,
			self._INTENT_ANSWER_YES_OR_NO: self.yesNoIntent
		}

		super().__init__(self._INTENTS, databaseSchema=self.DATABASE)

		self._minigames = dict()
		self._minigame: MiniGame = None

		for game in self._SUPPORTED_GAMES:
			try:
				lib = importlib.import_module(f'modules.Minigames.model.{game}')
				klass = getattr(lib, game)
				minigame = klass()
				self._INTENTS = {**self._INTENTS, **dict.fromkeys(minigame.intents, self.minigameIntent)}
			except Exception as e:
				self.logError(f'Something went wrong loading the minigame "{game}": {e}')


	def onSessionTimeout(self, session: DialogSession):
		if self._minigame:
			self._minigame.started = False


	def onUserCancel(self, session: DialogSession):
		if self._minigame:
			self._minigame.started = False

	def minigameIntent(self, intent: str, session: DialogSession) -> bool:
		self._minigame.onMessage(intent, session)
		return True

	def playGameIntent(self, intent: str, session: DialogSession) -> bool:
		sessionId = session.sessionId
		slots = session.slots

		if not self._minigame or not self._minigame.started:
			if 'WhichGame' not in slots:
				self.continueDialog(
					sessionId=sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME],
					text=self.TalkManager.randomTalk('whichGame'),
					previousIntent=self._INTENT_PLAY_GAME
				)

			elif session.slotValue('WhichGame') not in self._SUPPORTED_GAMES:
				self.continueDialog(
					sessionId=sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME, self._INTENT_ANSWER_YES_OR_NO],
					text=self.TalkManager.randomTalk('unknownGame'),
					previousIntent=self._INTENT_PLAY_GAME
				)

			else:
				game = session.slotValue('WhichGame')
				self._minigame = self._minigames[game]
				self._minigame.start(session)

		elif self._minigame is not None:
			self._minigame.onMessage(intent, session)
		return True


	def answerMinigameIntent(self, intent: str, session: DialogSession) -> bool:
		if session.previousIntent == self._INTENT_PLAY_GAME:
			return playGameIntent(intent=intent, session=session)
		return False


	def yesNoIntent(self, intent: str, session: DialogSession) -> bool:
		sessionId = session.sessionId

		if not self._minigame or not self._minigame.started:
			if not self.Commons.isYes(session):
				self.endDialog(
					sessionId=sessionId,
					text=self.randomTalk('endPlaying')
				)
			else:
				self.continueDialog(
					sessionId=sessionId,
					intentFilter=[self._INTENT_ANSWER_MINI_GAME],
					text=self.TalkManager.randomTalk('whichGame'),
					previousIntent=self._INTENT_PLAY_GAME
				)
		
		elif self._minigame is not None and session.customData and 'askRetry' in session.customData.keys():
			if self.Commons.isYes(session):
				self._minigame.start(session)
			else:
				self._minigame = None
				self.endDialog(
					sessionId=sessionId,
					text=self.randomTalk('endPlaying')
				)

		return False


	def checkAndStoreScore(self, user: str, score: int, biggerIsBetter: bool = True) -> bool:
		lastScore = self.databaseFetch(tableName='highscores', query='SELECT * FROM :__table__ WHERE username = :username ORDER BY score DESC LIMIT 1', values={'username': user})
		self.databaseInsert(
			tableName='highscores',
			query='INSERT INTO :__table__ (username, score, timestamp) VALUES (:username, :score, :timestamp)',
			values={'username': user, 'score': score, 'timestamp': round(time.time())}
		)

		if lastScore:
			if biggerIsBetter and score > int(lastScore['score']):
				return True
			elif not biggerIsBetter and score < int(lastScore['score']):
				return True
			else:
				return False

		else:
			return True
