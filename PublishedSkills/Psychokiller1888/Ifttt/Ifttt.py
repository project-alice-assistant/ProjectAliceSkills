import requests
from enum import Enum

from core.base.model.AliceSkill import AliceSkill


class IftttException(Enum):
	NOT_CONNECTED = 1
	BAD_REQUEST = 2
	NO_USER = 3
	ERROR = 4
	OK = 200


class Ifttt(AliceSkill):
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
		super().__init__(databaseSchema=self.DATABASE)


	# noinspection SqlResolve
	def sendRequest(self, endPoint: str, user: str, siteId: str) -> IftttException:
		if not self.InternetManager.online:
			return IftttException.NOT_CONNECTED

		try:
			result = self.databaseFetch(tableName='ifttt', query='SELECT * FROM :__table__ WHERE user = :user', values={'user': user.lower()})

			if result:
				answer = requests.post(url=f"https://maker.ifttt.com/trigger/{endPoint}/with/key/{result['key']}")
				return IftttException.OK if answer.status_code == 200 else IftttException.BAD_REQUEST

			return IftttException.NO_USER
		except Exception as e:
			self.logError(f'Error trying to request api: {e}')
			return IftttException.ERROR
