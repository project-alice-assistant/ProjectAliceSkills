import re

class dialogTemplate():
	def __init__(self, dialogTemplate: dict):
		self.dialogTemplate = dialogTemplate

	@property
	def slots(self) -> dict:
		slots = {}
		for slot in self.dialogTemplate['slotTypes']:
			slots[slot['name']] = slot
		return slots

	@property
	def intents(self) -> dict:
		intents = {}
		for intent in self.dialogTemplate['intents']:
			intents[intent['name']] = intent
		return intents

	@property
	def shortUtterances(self) -> dict:
		def upper_repl(match):
			return match.group(1).upper()
		
		utterancesDict = {}
		for intentName, intents in self.intents.items():
			utterancesDict[intentName] = {}
			for utterance in intents['utterances']:
				# make utterance lower case, slot name upper case, remove everything but characters and numbers
				# and make sure there is only one whitespace between two words
				short_utterance = utterance.lower()
				short_utterance = re.sub(r'{.*?:=>(.*?)}', upper_repl, short_utterance)
				short_utterance = re.sub(r'[^a-zA-Z1-9 ]', '', short_utterance)
				short_utterance = " ".join(short_utterance.split())
				# check whether the utterance already appeared and either add it to the list of duplicates
				# or mark that it appeared the first time
				if short_utterance in utterancesDict[intentName]:
					utterancesDict[intentName][short_utterance].append(utterance)
				else:
					utterancesDict[intentName][short_utterance] = [utterance]
		return utterancesDict
	
	@property
	def utteranceSlots(self) -> dict:
		utteranceSlotDict = {}
		for intentName, intents in self.intents.items():
			utteranceSlotDict[intentName] = {}
			for utterance in intents['utterances']:
				# search slots in utterances
				#r'{(.*?):=>(.*?)}')
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
