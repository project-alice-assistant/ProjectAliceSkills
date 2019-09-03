import core.base.Managers as managers
from core.base.Manager import Manager
from lnetatmo import WeatherStationData, ClientAuth


class WeatherStationDataExtended(WeatherStationData):

	def __init__(self, clientAuth: ClientAuth):
		super().__init__(clientAuth)


	
