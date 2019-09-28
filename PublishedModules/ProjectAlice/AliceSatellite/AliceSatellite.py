from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
import spacy


class AliceSatellite(Module):
	_INTENT_TEMPERATURE = Intent('GetTemperature')
	_INTENT_HUMIDITY = Intent('GetHumidity')
	_INTENT_CO2 = Intent('GetCo2Level')
	_INTENT_PRESSURE = Intent('GetPressure')

	_FEEDBACK_SENSORS = 'projectalice/devices/alice/sensorsFeedback'
	_DEVICE_DISCONNECTION = 'projectalice/devices/alice/disconnection'


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._FEEDBACK_SENSORS,
			self._INTENT_TEMPERATURE,
			self._INTENT_HUMIDITY,
			self._INTENT_CO2,
			self._INTENT_PRESSURE,
			self._DEVICE_DISCONNECTION
		]

		self._temperatures = dict()
		self._sensorReadings = dict()

		self.ProtectedIntentManager.protectIntent(self._FEEDBACK_SENSORS)
		self.ProtectedIntentManager.protectIntent(self._DEVICE_DISCONNECTION)

		super().__init__(self._SUPPORTED_INTENTS)
		self._nlp = spacy.load(self.LanguageManager.activeLanguage)


	def onBooted(self):
		confManager = SuperManager.getInstance().configManager
		if confManager.configAliceExists('onReboot') and confManager.getAliceConfigByName('onReboot') == 'greetAndRebootModules':
			self.restartDevice()


	def onSleep(self):
		self.broadcast('projectalice/devices/sleep')


	def onWakeup(self):
		self.broadcast('projectalice/devices/wakeup')


	def onGoingBed(self):
		self.broadcast('projectalice/devices/goingBed')


	def onFullMinute(self):
		self.getSensorReadings()


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		if 'Place' in slots:
			place = slots['Place']
			placeAnswer = self.roomAnswer(session.payload['input'], noun=place)
		else:
			place = siteId

		if intent == self._INTENT_TEMPERATURE:
			temp = self.getSensorValue(place, 'temperature')

			if temp == 'undefined':
				return False

			if place != siteId:
				self.endDialog(sessionId, self.randomTalk('temperaturePlaceSpecific').format(placeAnswer, temp.replace('.0', '')))
			else:
				self.endDialog(sessionId, self.randomTalk('temperature').format(temp.replace('.0', '')))

			return True

		elif intent == self._INTENT_HUMIDITY:
			humidity = self.getSensorValue(place, 'humidity')

			if humidity == 'undefined':
				return False
			else:
				humidity = int(round(float(humidity), 0))

			if place != siteId:
				self.endDialog(sessionId, self.randomTalk(text='humidityPlaceSpecific', replace=[placeAnswer, humidity]))
			else:
				self.endDialog(sessionId, self.randomTalk(text='humidity', replace=[humidity]))

			return True

		elif intent == self._INTENT_CO2:
			co2 = self.getSensorValue(place, 'gas')

			if co2 == 'undefined':
				return False

			if place != siteId:
				self.endDialog(sessionId, self.TalkManager.randomTalk('co2PlaceSpecific').format(placeAnswer, co2))
			else:
				self.endDialog(sessionId, self.TalkManager.randomTalk('co2').format(co2))

			return True

		elif intent == self._INTENT_PRESSURE:
			pressure = self.getSensorValue(place, 'pressure')

			if pressure == 'undefined':
				return False
			else:
				pressure = int(round(float(pressure), 0))

			if place != siteId:
				self.endDialog(sessionId, self.randomTalk(text='pressurePlaceSpecific', replace=[placeAnswer, pressure]))
			else:
				self.endDialog(sessionId, self.randomTalk(text='pressure', replace=[pressure]))

			return True

		elif intent == self._FEEDBACK_SENSORS:
			payload = session.payload
			if 'data' in payload:
				self._sensorReadings[siteId] = payload['data']
			return True

		elif intent == self._DEVICE_DISCONNECTION:
			payload = session.payload
			if 'uid' in payload:
				self.DeviceManager.deviceDisconnecting(payload['uid'])

		return False


	def getSensorReadings(self):
		self.broadcast('projectalice/devices/alice/getSensors')


	def temperatureAt(self, siteId: str) -> str:
		return self.getSensorValue(siteId, 'temperature')


	def getSensorValue(self, siteId: str, value: str) -> str:
		if siteId not in self._sensorReadings.keys():
			return 'undefined'

		data = self._sensorReadings[siteId]
		if value in data:
			ret = data[value]
			return ret
		else:
			return 'undefined'


	def restartDevice(self):
		devices = self.DeviceManager.getDevicesByType(deviceType=self.name, connectedOnly=True, onlyOne=False)
		if not devices:
			return

		for device in devices:
			self.publish(topic='projectalice/devices/restart', payload={'uid': device.uid})

	def roomAnswer(self, rawtext: str, noun: str) -> str:
    	# will be placed in a onLanguageChanged event since it takes about 0.4 seconds to load a new language
    	# -> would be good not to let the user wait longer than required
		lang = self.LanguageManager.activeLanguage
    	if lang != nlp.lang:
    	    nlp = spacy.load(lang)

    	nouns = allNouns = noun.lower().split()

    	for nounChunk in nlp(rawtext).noun_chunks:
    	    # search for room in noun chunk (can be mutliple parts e.g. 'living room') -> search them all
    	    for chunk in nounChunk:
    	        if chunk.pos_ == 'NOUN' and chunk.text.lower() in nouns:
    	            nouns.remove(chunk.text.lower())

    	    # when not all nouns found reset them
    	    if nouns:
    	        nouns = allNouns
    	        continue
			
    	    # depending on the language there are different grammatical structures to parse
    	    if(lang == 'de'):
    	        # preposition with article e.g. 'in dem' -> 'im'
    	        if nounChunk.root.head.tag_ == 'APPRART':
    	            return '{} {}'.format(nounChunk.root.head.text, noun)
    	        # only preposition e.g. 'im'
    	        elif nounChunk.root.head.tag_ == 'APPR':
    	            for chunk in nounChunk:
    	                if chunk.pos_ == 'DET':
    	                    det = '{} {}'.format(nounChunk.root.head.text, chunk.text)
    	                    # there are some preposition + article combinations, that get combined in german
    	                    combined = { 'an dem': 'am', 'in dem': 'im', 'zu dem': 'zum', 'zu der': 'zur'}
    	                    return '{} {}'.format(combined.get(det, det), noun)
    	            # fallback that works without knowing article and preposition
    	            return 'am Modul {}'.format(noun)
    	    elif(lang == 'en'):
    	        # preposition e.g. 'in' or 'on'
    	        if nounChunk.root.head.tag_ == 'IN':
    	            return '{} the {}'.format(nounChunk.root.head.text, noun)
    	        # fallback that works without knowing the preposition
    	        return 'at the module {}'.format(noun)
			elif (lang == 'fr'):
				#TODO implement french grammar (right now still just returns noun -> still old sentences)
				return noun
	
    	# when the 'room' is no noun but a adverb it can be directly used
    	return noun
