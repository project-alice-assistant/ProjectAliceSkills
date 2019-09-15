import time

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


	def onFullMinute(self):
		self._weatherData = lnetatmo.WeatherStationData(self._netatmoAuth)

		now = time.time()
		for siteId, value in self._weatherData.lastData().items():
			if 'Temperature' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.TEMPERATURE, value=value['Temperature'], service=self.name, siteId=siteId, timestamp=now)

			if 'CO2' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.CO2, value=value['CO2'], service=self.name, siteId=siteId, timestamp=now)

			if 'Humidity' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.HUMIDITY, value=value['Humidity'], service=self.name, siteId=siteId, timestamp=now)

			if 'Noise' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.NOISE, value=value['Noise'], service=self.name, siteId=siteId, timestamp=now)

			if 'Pressure' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.PRESSURE, value=value['Pressure'], service=self.name, siteId=siteId, timestamp=now)

			if 'Rain' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.RAIN, value=value['Rain'], service=self.name, siteId=siteId, timestamp=now)

			if 'sum_rain_1' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.SUM_RAIN_1, value=value['sum_rain_1'], service=self.name, siteId=siteId, timestamp=now)

			if 'sum_rain_24' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.SUM_RAIN_24, value=value['sum_rain_24'], service=self.name, siteId=siteId, timestamp=now)

			if 'WindStrength' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.WIND_STRENGTH, value=value['WindStrength'], service=self.name, siteId=siteId, timestamp=now)

			if 'WindAngle' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.WIND_ANGLE, value=value['WindAngle'], service=self.name, siteId=siteId, timestamp=now)

			if 'GustStrength' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.GUST_STRENGTH, value=value['GustStrength'], service=self.name, siteId=siteId, timestamp=now)

			if 'GustAngle' in value:
				self.TelemetryManager.storeData(ttype=TelemetryType.GUST_ANGLE, value=value['GustAngle'], service=self.name, siteId=siteId, timestamp=now)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		return False
