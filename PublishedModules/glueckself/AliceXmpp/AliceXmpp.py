import json

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class AliceXmpp(Module):
	"""
	Author: glueckself
	Description: Chat with alice via xmpp (jabber)
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		return True