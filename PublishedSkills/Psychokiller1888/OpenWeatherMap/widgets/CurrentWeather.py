import sqlite3

from core.base.model.Widget import Widget


class CurrentWeather(Widget):

	SIZE = 'w_small'
	OPTIONS = dict()

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def baseData(self) -> dict:
		return {
			'location': self.skillInstance.getConfig('baseLocation').title(),
			'units': 'C' if self.skillInstance.getConfig('units') == 'metric' else 'F' if self.skillInstance.getConfig('units') == 'imperial' else 'K',
			'unitsName': self.skillInstance.getConfig('units'),
			'apiKey': self.skillInstance.getConfig('apiKey')
		}
