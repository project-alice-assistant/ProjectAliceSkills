import sqlite3

from core.base.model.Widget import Widget


class CurrentWeather(Widget):

	SIZE = 'w_small'
	OPTIONS = dict()

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def baseData(self) -> dict:
		return {
			'location': self.myModule.getConfig('baseLocation').title(),
			'units': 'C' if self.myModule.getConfig('units') == 'metric' else 'F' if self.myModule.getConfig('units') == 'imperial' else 'K',
			'unitsName': self.myModule.getConfig('units'),
			'apiKey': self.myModule.getConfig('apiKey')
		}
