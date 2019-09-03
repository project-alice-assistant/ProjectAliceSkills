import requests
from enum import Enum

import core.base.Managers as managers
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class IftttException(Enum):
	NOT_CONNECTED = 1
	BAD_REQUEST = 2
	NO_USER = 3
	ERROR = 4
	OK = 200


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


	# noinspection SqlResolve
	def sendRequest(self, endPoint: str, user: str, siteId: str) -> IftttException:
		if not managers.InternetManager.online:
			return IftttException.NOT_CONNECTED

		try:
			result = self.databaseFetch(tableName='ifttt', query='SELECT * FROM :__table__ WHERE user = :user', values={'user': user.lower()})

			if result:
				answer = requests.post(url='https://maker.ifttt.com/trigger/{}/with/key/{}'.format(endPoint, result['key']))
				return IftttException.OK if answer.status_code == 200 else IftttException.BAD_REQUEST

			return IftttException.NO_USER
		except Exception as e:
			self._logger.error('[{}] Error trying to request api: {}'.format(self.name, e))
			return IftttException.ERROR


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		return False
