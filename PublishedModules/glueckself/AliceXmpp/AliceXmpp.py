import json

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from paho.mqtt.client import MQTTMessage
from core.commons import constants
from core.ProjectAliceExceptions import ModuleStartingFailed

import sleekxmpp
from sleekxmpp.xmlstream import stanzabase

# this code is from the sleekxmpp example. not sure if we need it
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

class ChatSession:
	def __init__(self, dialog: DialogSession, msg: dict):
		self.dialog = dialog
		self.msg = msg

class AliceXmpp(Module):
	"""
	Author: glueckself
	Description: Chat with alice via xmpp (jabber)
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
		]
		super().__init__(self._SUPPORTED_INTENTS)

		# touple (from, sessionId, msg)
		self._sessions = dict()

		jid = self.getConfig('aliceXmppJid')
		password = self.getConfig('aliceXmppPassword')
		self._xmpp = AliceXmppClient(jid, password)
		
		authorizedJids = self.getConfig('aliceXmppAuthorizedJids')
		self._xmpp.authorize(authorizedJids)
		
		server = self.getConfig('aliceXmppServer')
		port = self.getConifg('aliceXmppPort')		
		ssl = self.getConfig('aliceXmppSSL')
		if ssl == 'legacy':
			self._xmpp.connect(server, port, reattempt=True, use_ssl=True)
		elif ssl == 'tls':
			self._xmpp.connect(server, port, reattempt=True, use_tls=True)
		elif ssl == 'none':
			self._xmpp.connect(server, port, reattempt=True)
		else:
			raise ModuleStartingFailed('Invalid value in aliceXmppSSL: must be legacy, tls, or none')
			
		self._thread = self.ThreadManager.newThread(
			name='AliceXmppClient',
			target=self._xmpp.process,
			kwargs = {'block': True},
			autostart=True
		)
	
	def _getSessionById(self, sessionId: str) -> ChatSession:
		return self._sessions[0]
	
	def _getSessionByJid(self, jid: str) -> ChatSession:
		return self._sessions[0]

	def onSay(self, session: DialogSession):
		text = session.payload['text']
		session = self._getSessionById(session.sessionId)
		self._xmpp.sendMessage(mto=session.siteId, mtext=text)
		
	def doDialog(self, jid: str, text: str):
		session = self._getSessionByJid(jid)
		
		if not session:
			session = self.DialogSessionManager.preSession(jid, 'TODO-USER')
			mqttMessage = MQTTMessage()
			session = self.DialogSessionManager.addSession(session.sessionId, mqttMessage)
		else:
			self._refreshSession(session)

		result = self.LanguageManager.sanitizeNluQuery(text)

		supportedIntents = session.intentFilter or self.ModuleManager.supportedIntents
		intentFilter = [intent.justTopic for intent in supportedIntents if isinstance(intent, Intent) and not intent.protected]

		# Add Global Intents
		intentFilter.append(Intent('GlobalStop').justTopic)
	
		self.MqttManager.publish(topic=constants.TOPIC_NLU_QUERY, payload={'id':session.sessionId, 'input': result, 'intentFilter': intentFilter, 'sessionId': session.sessionId})
		
	def _refreshSession(self, session: DialogSession):
		pass

class AliceXmppClient(sleekxmpp.ClientXMPP):
	def __init__(self, alice, jid, password):
		self._alice = alice
		self._myJid = jid
		self._authorizedJids = dict()

		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('xep_0004') # Data Forms
		self.register_plugin('xep_0060') # PubSub
		self.register_plugin('xep_0199') # XMPP Ping

		self.add_event_handler('session_start', self.start)
		self.add_event_handler('message', self.message)
		
	def start(self, event):
		self.send_presence()
		self.get_roster()

	def message(self, msg):
		if msg['type'] not in ('chat', 'normal'):
			return
		sender = msg['from'].bare
		if sender not in self._authorizedJids:
			return
		
		self.alice.doDialog(sender, msg['text'])

	def authorize(self, jids: dict):
		self.authorizedJids.append(jids)

