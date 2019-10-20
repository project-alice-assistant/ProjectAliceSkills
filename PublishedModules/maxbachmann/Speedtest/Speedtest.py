import speedtest
from speedtest import SpeedtestException

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
		self.ThreadManager.doLater(interval=0, func=self.executeSpeedtest, kwargs={'session': session})
		self.logInfo('Starting Speedtest')
		self.endDialog(sessionId=session.sessionId, text=self.randomTalk('running'))


	@Decorators.anyExcept(exceptions=(SpeedtestException, KeyError), text='failed', printStack=True)
	@Decorators.online
	def executeSpeedtest(self, session: DialogSession):
		speed = speedtest.Speedtest()
		speed.get_servers()
		speed.get_best_server()
		speed.download()
		speed.upload(pre_allocate=False)
		speed.results.share()
		result = speed.results.dict()
		downspeed = '{:.2f}'.format(result['download']/1000000)
		upspeed = '{:.2f}'.format(result['upload']/1000000)
		self.logInfo(f'Download speed: {downspeed} Mbps, Upload speed: {upspeed} Mbps')
		self.say(text=self.randomTalk(text='result', replace=[downspeed, upspeed]), siteId=session.siteId)
