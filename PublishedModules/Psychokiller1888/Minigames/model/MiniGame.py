import logging

from abc import ABCMeta, abstractmethod

from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.dialog.model import DialogSession
from core.snips.samkilla.Intent import Intent


class MiniGame(ProjectAliceObject, metaclass=ABCMeta):

	_INTENT_PLAY_GAME = Intent('PlayGame')

	def __init__(self):
		super().__init__(logDepth=4)
		self._started = False


	@property
	def started(self) -> bool:
		return self._started


	@started.setter
	def started(self, value: bool):
		self._started = value


	@property
	@abstractmethod
	def intents(self) -> list:
		pass


	@abstractmethod
	def start(self, session: DialogSession):
		self._started = True


	@abstractmethod
	def onMessage(self, intent: str, session: DialogSession):
		pass
