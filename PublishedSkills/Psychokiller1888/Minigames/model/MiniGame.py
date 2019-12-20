import time
from pathlib import Path

from core.base.SuperManager import SuperManager
from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.dialog.model import DialogSession


class MiniGame(ProjectAliceObject):

	_INTENT_PLAY_GAME = 'PlayGame'
	_INTENT_ANSWER_YES_OR_NO = 'AnswerYesOrNo'

	PLAYING_MINIGAME_STATE = 'playingMiniGame'
	ANSWERING_PLAY_AGAIN_STATE = 'answeringPlayAgain'

	def __init__(self):
		super().__init__(logDepth=4)
		self._started = False
		self._intents = list()


	def onMessage(self, session) -> bool:
		pass


	@property
	def started(self) -> bool:
		return self._started


	@started.setter
	def started(self, value: bool):
		self._started = value


	@property
	def intents(self) -> list:
		return self._intents


	def start(self, session: DialogSession):
		self._started = True


	# noinspection SqlResolve
	def checkAndStoreScore(self, user: str, score: int, biggerIsBetter: bool = True) -> bool:
		lastScore = self.DatabaseManager.databaseFetch(
			tableName='highscores',
			query='SELECT * FROM :__table__ WHERE username = :username ORDER BY score DESC LIMIT 1',
			values={'username': user}
		)

		self.DatabaseManager.databaseInsert(
			tableName='highscores',
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


	@staticmethod
	def sound(filename: str, siteId: str):
		SuperManager.getInstance().mqttManager.playSound(
			soundFilename=filename,
			location=Path(f'{SuperManager.getInstance().commons.rootDir()}/skills/Minigames/sounds'),
			sessionId=filename,
			siteId=siteId
		)
