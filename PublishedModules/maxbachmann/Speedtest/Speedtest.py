import speedtest

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.commons import online

class Speedtest(Module):
	"""
	Author: maxbachmann
	Description: run internet speed test
	"""

	_INTENT_SPEEDTEST = Intent('Speedtest')

	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_SPEEDTEST
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_SPEEDTEST:
			self.endDialog(sessionId=session.sessionId, text=self.runSpeedtest())
		return True

	@online
	def runSpeedtest(self) -> str:
		self.ThreadManager.doLater(interval=0, func=self.executeSpeedtest)
		self._logger.info('[{}] Starting Speedtest'.format(self.name))
		return self.randomTalk('running')

	def executeSpeedtest(self):
		try:
			servers: list = list()
			speed = speedtest.Speedtest()
			speed.get_servers(servers)
			speed.get_best_server()
			speed.download()
			speed.upload(pre_allocate=False)
			speed.results.share()
			result = speed.results.dict()
			downspeed = '{:.2f}'.format(result['download']/1000000)
			upspeed = '{:.2f}'.format(result['upload']/1000000)
			self._logger.info('[{}] Download speed: {} Mbps, Upload speed: {} Mbps'.format(self.name, downspeed, upspeed))
			self.say(text=self.randomTalk(text='result', replace=[downspeed, upspeed]))
		except Exception as e:
			self.say(self.randomTalk(text='failed'))
			self._logger.warning('[{}] Download failed with: {}'.format(self.name, e))
