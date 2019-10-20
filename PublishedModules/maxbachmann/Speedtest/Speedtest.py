import speedtest

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators

class Speedtest(Module):
	"""
	Author: maxbachmann
	Description: run internet speed test
	"""

	_INTENT_SPEEDTEST = Intent('Speedtest')

	def __init__(self):
		self._INTENTS = [
			(self._INTENT_SPEEDTEST, self.runSpeedtest)
		]

		super().__init__(self._INTENTS)


	@Decorators.online
	def runSpeedtest(self, session: DialogSession, **_kwargs):
		self.ThreadManager.doLater(interval=0, func=self.executeSpeedtest)
		self.logInfo('Starting Speedtest')
		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('running'))


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
			self.logInfo(f'Download speed: {downspeed} Mbps, Upload speed: {upspeed} Mbps')
			self.say(text=self.randomTalk(text='result', replace=[downspeed, upspeed]))
		except Exception as e:
			self.say(self.randomTalk(text='failed'))
			self.logWarning(f'Speedtest failed with: {e}')
