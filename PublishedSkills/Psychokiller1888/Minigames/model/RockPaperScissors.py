import random

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.dialog.model.DialogSession import DialogSession
from .MiniGame import MiniGame


class RockPaperScissors(MiniGame):

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

		SuperManager.getInstance().mqttManager.continueDialog(
			sessionId=session.sessionId,
			text=SuperManager.getInstance().talkManager.randomTalk(talk='rockPaperScissorsStart', skill='Minigames'),
			intentFilter=[self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS],
			previousIntent=self._INTENT_PLAY_GAME
		)


	def onMessage(self, session: DialogSession):
		if session.intentName == self._INTENT_ANSWER_ROCK_PAPER_OR_SCISSORS:
			choices = ['rock', 'paper', 'scissors']
			me = random.choice(choices)

			self.sound('drum_suspens', session.siteId)

			redQueen = SuperManager.getInstance().skillManager.getSkillInstance('RedQueen')
			redQueen.changeRedQueenStat('happiness', 5)
			player = session.slotValue('RockPaperOrScissors')
			# tie
			if player == me:
				result = 'rockPaperScissorsTie'
			# player wins
			elif choices[choices.index(player) - 1] == me:
				result = 'rockPaperScissorsWins'
				redQueen.changeRedQueenStat('frustration', 2)
			# alice wins
			else:
				result = 'rockPaperScissorsLooses'
				redQueen.changeRedQueenStat('frustration', -5)
				redQueen.changeRedQueenStat('happiness', 5)

			SuperManager.getInstance().mqttManager.continueDialog(
				sessionId=session.sessionId,
				text=SuperManager.getInstance().talkManager.randomTalk(
					talk=result,
					skill='Minigames'
				).format(SuperManager.getInstance().languageManager.getTranslations(skill='Minigames', key=me, toLang=SuperManager.getInstance().languageManager.activeLanguage)[0]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				previousIntent=self._INTENT_PLAY_GAME,
				customData={
					'askRetry': True
				}
			)
