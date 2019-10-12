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
		self._INTENTS = {
			self._INTENT_SPEEDTEST: self.runSpeedtest
		}

		super().__init__(self._INTENTS)


	def offlineHandler(self, session: DialogSession, **kwargs) -> bool:
		self.endDialog(session.sessionId, text=self.TalkManager.randomTalk('offline', module='system'))
		return True


	@online(offlineHandler=offlineHandler)
	def runSpeedtest(self, intent: str, session: DialogSession) -> bool:
		self.ThreadManager.doLater(interval=0, func=self.executeSpeedtest)
		self._logger.info(f'[{self.name}] Starting Speedtest')
		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('running'))
		return True


	def executeSpeedtest(self):
		try:
			servers = list()
			speed = speedtest.Speedtest()
			speed.get_servers(servers)
			speed.get_best_server()
			speed.download()
			speed.upload(pre_allocate=False)
			speed.results.share()
			result = speed.results.dict()
			downspeed = '{:.2f}'.format(result['download']/1000000)
			upspeed = '{:.2f}'.format(result['upload']/1000000)
			self._logger.info(f'[{self.name}] Download speed: {downspeed} Mbps, Upload speed: {upspeed} Mbps')
			self.say(text=self.randomTalk(text='result', replace=[downspeed, upspeed]))
		except Exception as e:
			self.say(self.randomTalk(text='failed'))
			self._logger.warning(f'[{self.name}] Speedtest failed with: {e}')
