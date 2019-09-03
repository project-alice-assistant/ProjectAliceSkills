import json
import time

import core.base.Managers as managers
from core.ProjectAliceExceptions import ModuleStartingFailed
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
import lnetatmo


class Netatmo(Module):
	"""
	Author: Psychokiller1888
	Description: Get readings from your netatmo hardware
	"""

	_INTENT_TEMPERATURE 				= Intent('GetTemperature')
	_INTENT_HUMIDITY 					= Intent('GetHumidity')
	_INTENT_CO2 						= Intent('GetCo2Level')
	_INTENT_NOISE_LEVEL 				= Intent('GetNoiseLevel')
	_INTENT_PRESSURE 					= Intent('GetPressure')
	_INTENT_WIND 						= Intent('GetWind')
	_INTENT_RAIN 						= Intent('GetRain')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_TEMPERATURE,
			self._INTENT_HUMIDITY,
			self._INTENT_CO2,
			self._INTENT_NOISE_LEVEL,
			self._INTENT_PRESSURE,
			self._INTENT_WIND,
			self._INTENT_RAIN
		]

		super().__init__(self._SUPPORTED_INTENTS)

		self._netatmoAuth 	= None
		self._weatherData 	= None
		self._authTries 	= 0


	def onStart(self) -> list:
		if not self.getConfig('password'):
			raise ModuleStartingFailed(moduleName=self.name, error='[{}] No credentials provided'.format(self.name))

		if self._auth():
			try:
				self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)
			except lnetatmo.NoDevice:
				raise ModuleStartingFailed(moduleName=self.name, error='[{}] No Netatmo device found'.format(self.name))
			else:
				return super().onStart()
		else:
			raise ModuleStartingFailed(moduleName=self.name, error='[{}] Authentication failed'.format(self.name))


	def _auth(self) -> bool:

		try:
			self._netatmoAuth = lnetatmo.ClientAuth(
				clientId=self.getConfig('clientId'),
				clientSecret=self.getConfig('clientSecret'),
				username=self.getConfig('username'),
				password=self.getConfig('password'),
				scope='read_station'
			)
		except lnetatmo.AuthFailure:
			self._authTries += 1
			if self._authTries >= 3:
				self._logger.warning('[{}] Tried to auth 3 times, giving up now'.format(self.name))
				return False
			else:
				time.sleep(1)
				return self._auth()

		return True


	def onFullMinute(self):
		if self._weatherData:
			self._weatherData.getMeasure()


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		return True
