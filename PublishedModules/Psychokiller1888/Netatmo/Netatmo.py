import time
from typing import Generator, Tuple

import lnetatmo

from core.ProjectAliceExceptions import ModuleStartingFailed
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.model.TelemetryType import TelemetryType


class Netatmo(Module):
	"""
	Author: Psychokiller1888
	Description: Get readings from your netatmo hardware
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= []

		super().__init__(self._SUPPORTED_INTENTS)

		self._netatmoAuth 	= None
		self._weatherData 	= None
		self._authTries 	= 0
		self._telemetryTypes = {
			'Temperature': TelemetryType.TEMPERATURE,
			'CO2': TelemetryType.CO2,
			'Humidity': TelemetryType.HUMIDITY,
			'Noise': TelemetryType.NOISE,
			'Pressure': TelemetryType.PRESSURE,
			'Rain': TelemetryType.RAIN,
			'sum_rain_1': TelemetryType.SUM_RAIN_1,
			'sum_rain_24': TelemetryType.SUM_RAIN_24,
			'WindStrength': TelemetryType.WIND_STRENGTH,
			'WindAngle': TelemetryType.WIND_ANGLE,
			'GustStrength': TelemetryType.GUST_STRENGTH,
			'GustAngle': TelemetryType.GUST_ANGLE
		}


	def onStart(self) -> list:
		super().onStart()
		if not self.getConfig('password'):
			raise ModuleStartingFailed(moduleName=self.name, error='[{}] No credentials provided'.format(self.name))

		if self._auth():
			try:
				self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)
			except lnetatmo.NoDevice:
				raise ModuleStartingFailed(moduleName=self.name, error='[{}] No Netatmo device found'.format(self.name))
			else:
				return self._SUPPORTED_INTENTS
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


	def _lastWeatherData(self) -> Generator[Tuple[str, str, str], None, None]:
		for siteId, values in self._weatherData.lastData().items():
			for key, value in values.items():
				yield (siteId, self._telemetryTypes.get(key), value)


	def onFullMinute(self):
		self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)

		now = time.time()
		for siteId, ttype, value in self._lastWeatherData():
			if ttype:
				self.TelemetryManager.storeData(ttype=ttype, value=value, service=self.name, siteId=siteId, timestamp=now)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		return False
