import re
from typing import Match
from collections import defaultdict

class DialogTemplate:

	def __init__(self, dialogTemplate: dict, verbosity: int = 0):
		self._dialogTemplate = dialogTemplate
		self._verbosity = verbosity
		self._slots = dict()
		self._intents = dict()
		self._cleanedUtterances = dict()
		self._utteranceSlots = dict()

		self._initSlots()
		self._initIntents()
		self._initCleanedUtterances()
		self._initUtteranceSlots()


	def _initSlots(self):
		for slot in self._dialogTemplate.get('slotTypes', dict()):
			self._slots[slot['name']] = slot


	def _initIntents(self):
		for intent in self._dialogTemplate.get('intents', dict()):
			self._intents[intent['name']] = intent


	def _cleanUtterance(self, utterance: str) -> str:
		def upperRepl(match: Match) -> str:
			return match.group(1).upper()

		cleanUtterance = utterance.lower()
		if self._verbosity:
			cleanUtterance = re.sub(r'{.*?:=>(.*?)}', upperRepl, cleanUtterance)
		cleanUtterance = re.sub(r'[^a-zA-Z1-9 ]', '', cleanUtterance)
		return ' '.join(cleanUtterance.split())


	def _initCleanedUtterances(self):
		for intentName, intents in self.intents.items():
			self._cleanedUtterances[intentName] = defaultdict(list)
			for utterance in intents['utterances']:
				self._cleanedUtterances[intentName][self._cleanUtterance(utterance)].append(utterance)


	def _mapUtteranceSlots(self, utterance: str, slots: list) -> defaultdict:
		utteranceSlotMapping = defaultdict(list)
		slotNames = re.findall(r'{(.*?):=>(.*?)}', utterance)
		for slot in slots:
			for slotValue, slotName in slotNames:
				if slot['name'] == slotName:
					utteranceSlotMapping[slot['type']].append(slotValue)

		return utteranceSlotMapping


	def _initUtteranceSlots(self):
		for intentName, intents in self.intents.items():
			for utterance in intents['utterances']:
				self._utteranceSlots[intentName] = self._mapUtteranceSlots(utterance, intents['slots'])


	@property
	def slots(self) -> dict:
		return self._slots


	@property
	def intents(self) -> dict:
		return self._intents


	@property
	def cleanedUtterances(self) -> dict:
		return self._cleanedUtterances


	@property
	def utteranceSlots(self) -> dict:
		return self._utteranceSlots
