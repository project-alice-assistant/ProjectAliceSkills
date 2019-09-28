import re


class DialogTemplate:

	def __init__(self, dialogTemplate: dict):
		self._dialogTemplate = dialogTemplate


	@property
	def slots(self) -> dict:
		slots = {}
		if self._dialogTemplate:
			for slot in self._dialogTemplate['slotTypes']:
				slots[slot['name']] = slot
		return slots


	@property
	def intents(self) -> dict:
		intents = {}
		if self._dialogTemplate:
			for intent in self._dialogTemplate['intents']:
				intents[intent['name']] = intent
		return intents


	@property
	def shortUtterances(self) -> dict:
		def upperRepl(match):
			return match.group(1).upper()


		utterancesDict = {}
		for intentName, intents in self.intents.items():
			utterancesDict[intentName] = {}
			for utterance in intents['utterances']:
				# make utterance lower case, slot name upper case, remove everything but characters and numbers
				# and make sure there is only one whitespace between two words
				shortUtterance = utterance.lower()
				shortUtterance = re.sub(r'{.*?:=>(.*?)}', upperRepl, shortUtterance)
				shortUtterance = re.sub(r'[^a-zA-Z1-9 ]', '', shortUtterance)
				shortUtterance = " ".join(shortUtterance.split())
				# check whether the utterance already appeared and either add it to the list of duplicates
				# or mark that it appeared the first time
				if shortUtterance in utterancesDict[intentName]:
					utterancesDict[intentName][shortUtterance].append(utterance)
				else:
					utterancesDict[intentName][shortUtterance] = [utterance]
		return utterancesDict


	@property
	def utteranceSlots(self) -> dict:
		utteranceSlotDict = {}
		for intentName, intents in self.intents.items():
			utteranceSlotDict[intentName] = {}
			for utterance in intents['utterances']:
				slotNames = re.findall(r'{(.*?):=>(.*?)}', utterance)
				for slot in intents['slots']:
					for value, slotName in slotNames:
						if slot['name'] == slotName:
							if slot['type'] in utteranceSlotDict[intentName]:
								if value not in utteranceSlotDict[intentName][slot['type']]:
									utteranceSlotDict[intentName][slot['type']].append(value)
							else:
								utteranceSlotDict[intentName][slot['type']] = [value]
		return utteranceSlotDict
