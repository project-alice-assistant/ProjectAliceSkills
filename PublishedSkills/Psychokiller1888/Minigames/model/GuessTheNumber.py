import time

import random

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class GuessTheNumber(MiniGame):

	_INTENT_PLAY_GAME = Intent('PlayGame')
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_ANSWER_NUMBER = Intent('AnswerNumber', isProtected=True)

	def __init__(self):
		super().__init__()
		self._number = 0
		self._start: float = 0


	@property
	def intents(self) -> list:
		return [
			self._INTENT_ANSWER_NUMBER
		]


	def start(self, session: DialogSession):
		super().start(session)

		redQueen = SuperManager.getInstance().skillManager.getSkillInstance('RedQueen')
		redQueen.changeRedQueenStat('happiness', 10)

		self._number = random.randint(1, 10000)

		self._start = time.time() - 4

		SuperManager.getInstance().mqttManager.continueDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(talk='guessTheNumberStart', skill='Minigames'),
			intentFilter=[self._INTENT_ANSWER_NUMBER],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, session: DialogSession):
		if session.intentName == self._INTENT_ANSWER_NUMBER:
			self.numberIntent(session)


	def numberIntent(self, session: DialogSession):
		number = int(session.slotValue('Number'))
		if number == self._number:

			score = round(time.time() - self._start)
			m, s = divmod(score, 60)
			scoreFormatted = SuperManager.getInstance().languageManager.getTranslations(skill='Minigames', key='minutesAndSeconds')[0].format(round(m), round(s))

			self.sound('applause', session.siteId)

			SuperManager.getInstance().mqttManager.endDialog(
				sessionId=session.sessionId,
				text=SuperManager.getInstance().talkManager.randomTalk('guessTheNumberCorrect', 'Minigames').format(self._number, self._number)
			)

			textType = 'guessTheNumberScore'
			if session.user != 'unknown' and SuperManager.getInstance().skillManager.getSkillInstance('Minigames').checkAndStoreScore(user=session.user, score=score, biggerIsBetter=False):
				textType = 'guessTheNumberNewHighscore'

			SuperManager.getInstance().mqttManager.say(
				client=session.siteId,
				text=SuperManager.getInstance().talkManager.randomTalk(textType, 'Minigames').format(scoreFormatted),
				canBeEnqueued=True
			)

			SuperManager.getInstance().mqttManager.ask(
				text=SuperManager.getInstance().talkManager.randomTalk('playAgain', 'Minigames'),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_PLAY_GAME,
				customData={
					'speaker': session.user,
					'askRetry': True
				}
			)
			return

		textType = 'guessTheNumberLess'
		if number < self._number:
			textType = 'guessTheNumberMore'

		SuperManager.getInstance().mqttManager.continueDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(textType, 'Minigames'),
			intentFilter=[self._INTENT_ANSWER_NUMBER],
			previousIntent=session.intentName
		)
