import json
import uuid

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from paho.mqtt.client import MQTTMessage
from core.commons import constants
from core.ProjectAliceExceptions import ModuleStartingFailed

import sleekxmpp
from sleekxmpp.xmlstream import stanzabase

class AliceXmpp(Module):
	"""
	Author: glueckself
	Description: Chat with alice via xmpp (jabber)
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
		]
		super().__init__(self._SUPPORTED_INTENTS)

		# maybe list of tuples (sessionId, jid)
		self._sessions = dict()

		jid = self.getConfig('aliceXmppJid')
		password = self.getConfig('aliceXmppPassword')
		self._xmpp = AliceXmppClient(self, jid, password)
		
		authorizedJids = self.getConfig('aliceXmppAuthorizedJids')
		self._xmpp.authorize(authorizedJids)
		self.ThreadManager.doLater(func=self._connectXmpp, interval=0)

	def _connectXmpp(self):
		server = self.getConfig('aliceXmppServer')
		port = self.getConfig('aliceXmppPort')
		ssl = self.getConfig('aliceXmppSSL')
		if ssl == 'legacy':
			self._xmpp.connect(address=(server, port), use_tls=False, use_ssl=True)
		elif ssl == 'tls':
			self._xmpp.connect(address=(server, port), use_tls=True)
		elif not ssl:
			self._xmpp.connect(address=(server, port), use_tls=False)
		else:
			raise ModuleStartingFailed('Invalid value in aliceXmppSSL: must be "legacy", "tls", or left empty')
			
		self._thread = self.ThreadManager.newThread(
			name='AliceXmppClient',
			target=self._xmpp.process,
			kwargs = {'block': True},
			autostart=True
		)

	def onStop(self):
		self._xmpp.disconnect(wait=True)
		super().onStop()
	
	def _getJidBySessionId(self, sessionId: str) -> str:
		for jid, _sessionId in self._sessions.items():
			if _sessionId == sessionId:
				return jid
		return None

	def onSay(self, session: DialogSession):
		breakpoint()
		text = session.payload['text']
		jid = self._getJidBySessionId(session.sessionId)
		if jid:
			self._xmpp.sendMessage(mto=jid, mtext=text)

	def onIntentParsed(self, session: DialogSession):
		if not self._getJidBySessionId(session.sessionId):
			return
		intent = Intent(session.payload['intent']['intentName'].split(':')[1])
		message = MQTTMessage(topic=str.encode(str(intent)))
		message.payload = json.dumps(session.payload)
		self.MqttManager.onMessage(client=None, userdata=None, message=message)

	def _closeChatSession(self, session):
		breakpoint()
		jid = self._getJidBySessionId(session.sessionId)
		if not jid:
			return
		self._xmpp.sendMessage(mto=jid, mtext='I\'m gone now, bye')
		del self._sessions[jid]

	def onSessionTimeout(self, session: DialogSession, *args, **kwargs):
		self._closeChatSession(session)

	def onSessionError(self, session: DialogSession, *args, **kwargs):
		self._closeChatSession(session)

	def onSessionEnded(self, session: DialogSession, *args, **kwargs):
		self._closeChatSession(session)

	def doDialog(self, jid: str, text: str):
		session = None
		if jid not in self._sessions:
			mesg = MQTTMessage()
			mesg.payload = f'{{"siteId": "{jid}"}}'
			session = self.DialogSessionManager.preSession(jid, 'sergio')
			session = self.DialogSessionManager.addSession(str(uuid.uuid4()), mesg)
			self._sessions[jid] = session.sessionId
		else:
			sessionId = self._sessions[jid]
			session = self.DialogSessionManager.getSession(sessionId)
			self._refreshSession(session)

		result = self.LanguageManager.sanitizeNluQuery(text)
		supportedIntents = session.intentFilter or self.ModuleManager.supportedIntents
		intentFilter = [intent.justTopic for intent in supportedIntents if isinstance(intent, Intent) and not intent.protected]
		# Add Global Intents
		intentFilter.append(Intent('GlobalStop').justTopic)
		self.MqttManager.publish(topic=constants.TOPIC_NLU_QUERY,
			payload={
				'siteId': jid,
				'input': result,
				'intentFilter': intentFilter,
				'id': session.sessionId,
				'sessionId': session.sessionId
			}
		)
		
	def _refreshSession(self, session: DialogSession):
		pass

	def _expireSession(self):
		pass

class AliceXmppClient(sleekxmpp.ClientXMPP):
	def __init__(self, alice, jid, password):
		self._alice = alice
		self._myJid = jid
		self._authorizedJids = list()

		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('xep_0004') # Data Forms
		self.register_plugin('xep_0060') # PubSub
		self.register_plugin('xep_0199') # XMPP Ping

		self.add_event_handler('session_start', self.start)
		self.add_event_handler('message', self.message)
		
	def start(self, event):
		self.get_roster()
		self.send_presence()

	def message(self, msg):
		if msg['type'] not in ('chat', 'normal'):
			return
		sender = msg['from'].bare
		if sender not in self._authorizedJids:
			return
		try:
			self._alice.doDialog(sender, msg['body'])
		except Exception as e:
			print(e)

	def authorize(self, jids: list):
		self._authorizedJids += jids

