import re
from typing import Match
from collections import defaultdict

class DialogTemplate:

	def __init__(self, dialogTemplate: dict):
		self._dialogTemplate = dialogTemplate


	@property
	def slots(self) -> dict:
		slots = dict()
		if self._dialogTemplate:
			for slot in self._dialogTemplate['slotTypes']:
				slots[slot['name']] = slot
		return slots


	@property
	def intents(self) -> dict:
		intents = dict()
		if self._dialogTemplate:
			for intent in self._dialogTemplate['intents']:
				intents[intent['name']] = intent
		return intents


	@property
	def shortUtterances(self) -> dict:
		def upperRepl(match: Match) -> str:
			return match.group(1).upper()

		utterancesDict: dict = dict()
		for intentName, intents in self.intents.items():
			utterancesDict[intentName] = defaultdict(list)
			for utterance in intents['utterances']:
				# make utterance lower case, slot name upper case, remove everything but characters and numbers
				# and make sure there is only one whitespace between two words
				shortUtterance = utterance.lower()
				shortUtterance = re.sub(r'{.*?:=>(.*?)}', upperRepl, shortUtterance)
				shortUtterance = re.sub(r'[^a-zA-Z1-9 ]', '', shortUtterance)
				shortUtterance = ' '.join(shortUtterance.split())
				utterancesDict[intentName][shortUtterance].append(utterance)
		return utterancesDict


	@property
	def utteranceSlots(self) -> dict:
		utteranceSlotDict: dict = dict()
		for intentName, intents in self.intents.items():
			utteranceSlotDict[intentName] = defaultdict(list)
			for utterance in intents['utterances']:
				slotNames = re.findall(r'{(.*?):=>(.*?)}', utterance)
				for slot in intents['slots']:
					for value, slotName in slotNames:
						if slot['name'] == slotName:
							utteranceSlotDict[intentName][slot['type']].append(value)
		return utteranceSlotDict
