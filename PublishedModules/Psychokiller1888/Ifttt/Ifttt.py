# -*- coding: utf-8 -*-

import requests
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Ifttt(Module):
	"""
	Author: Psychokiller1888
	Description: Use ifttt services
	"""

	DATABASE = {
		'ifttt': [
			'id integer PRIMARY KEY',
			'user TEXT NOT NULL',
			'key TEXT NOT NULL'
		]
	}

	def __init__(self):
		self._SUPPORTED_INTENTS	= []

		super().__init__(self._SUPPORTED_INTENTS, self.DATABASE)


	def sendRequest(self, endPoint: str, user: str) -> bool:
		try:
			result = self.databaseFetch(tableName='ifttt', query='SELECT key FROM :__table__ WHERE user = :user', values={'user': user})
			if result:
				requests.post(url='https://maker.ifttt.com/trigger/{}/with/key/{}'.format(endPoint, result[0]['key']))
				return True
			return False
		except Exception as e:
			self._logger.error('[{}] Error trying to request api: {}'.format(self.name, e))


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		return False
