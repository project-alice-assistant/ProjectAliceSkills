import sqlite3

from core.base.SuperManager import SuperManager
from core.base.model.Widget import Widget


class WhosAboard(Widget):

	SIZE = 'w_tall'
	OPTIONS: dict = dict()

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)
