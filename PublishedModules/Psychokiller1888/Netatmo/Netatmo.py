import time
from typing import Tuple

import lnetatmo

from core.ProjectAliceExceptions import ModuleStartingFailed
from core.base.model.Module import Module
from core.util.model.TelemetryType import TelemetryType


class Netatmo(Module):
	"""
	Author: Psychokiller1888
	Description: Get readings from your netatmo hardware
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= list()

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
			raise ModuleStartingFailed(moduleName=self.name, error='No credentials provided')

		if not self._auth():
			raise ModuleStartingFailed(moduleName=self.name, error='Authentication failed')

		try:
			self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)
		except lnetatmo.NoDevice:
			raise ModuleStartingFailed(moduleName=self.name, error='No Netatmo device found')
		else:
			return self._SUPPORTED_INTENTS


	def _auth(self) -> bool:
		try:
			self._netatmoAuth = lnetatmo.ClientAuth(
				clientId=self.getConfig('clientId'),
				clientSecret=self.getConfig('clientSecret'),
				username=self.getConfig('username'),
				password=self.getConfig('password'),
				scope='read_station'
			)
		except Exception:
			self._authTries += 1
			if self._authTries >= 3:
				self.logWarning('Tried to auth 3 times, giving up now')
				raise ModuleStartingFailed
			else:
				time.sleep(1)
				return self._auth()

		return True


	def _lastWeatherData(self) -> Tuple[str, str, str]:
		self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)
		for siteId, values in self._weatherData.lastData().items():

			if siteId == 'Wind' or siteId == 'Rain':
				siteId = self.LanguageManager.getStrings('outside')[0]

			for key, value in values.items():
				yield (siteId.lower(), self._telemetryTypes.get(key), value)


	def onFullMinute(self):
		now = time.time()
		for siteId, ttype, value in self._lastWeatherData():
			if ttype:
				self.TelemetryManager.storeData(ttype=ttype, value=value, service=self.name, siteId=siteId, timestamp=now)
