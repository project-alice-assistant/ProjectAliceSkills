import os
import glob
import json
import re
from validation import validation

class dialogValidation(validation):
	
	@property
	def JsonSchema(self) -> dict:
		with open(os.path.join(self.dir_path, 'dialog-schema.json') ) as json_file:
			return json.load(json_file)
	
	@property
	def JsonFiles(self) -> list:
		return glob.glob( os.path.join(self.modulePath, 'dialogTemplate/*.json') )

	def getSlots(self, file: str) -> tuple:
		valid, data = self.validateSyntax(file)
		if valid:
			slots = {}
			for slot in data['slotTypes']:
				slots[slot['name']] = slot
			data = slots
		return (valid, data)

	def getTrainingExamples(self, file: str) -> tuple:
		valid, data = self.validateSyntax(file)
		if valid:
			trainingExamples = {}
			for intent in data['intents']:
				trainingExamples[intent['name']] = intent['utterances']
			data = trainingExamples
		return (valid, data)

	def validateSlots(self) -> bool:
		err = 0
		all_slots = {}
		
		# get slots from all json files of a module
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.getSlots(file)
			if not valid:
				err = 1
				continue
			all_slots.update(data)

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.getSlots(file)
			if not valid:
				err = 1
				continue

			self.validModule['slots'][self.filename(file)] = [k for k, v in all_slots.items() if k not in data]
			if self.validModule['slots'][self.filename(file)]:
				err = 1
		return err

	def searchDuplicateUtterances(self) -> bool:
		def upper_repl(match):
			return match.group(1).upper()

		err = 0
		for file in self.JsonFiles:
			jsonPath = self.validModule['utterances'][self.filename(file)]['duplicates']
			# get data and check whether it is valid
			valid, data = self.getTrainingExamples(file)
			if not valid:
				err = 1
				continue

			for intentName, utterances in data.items():
				utterancesDict = {}
				for utterance in utterances:
					# make utterance lower case, slot name upper case, remove everything but characters and numbers
					# and make sure there is only one whitespace between two words
					short_utterance = utterance.lower()
					short_utterance = re.sub(r'{[^:=>]*:=>([^}]*)}', upper_repl, short_utterance)
					short_utterance = re.sub(r'[^a-zA-Z1-9 ]', '', short_utterance)
					short_utterance = " ".join(short_utterance.split())
					# check whether the utterance already appeared and either add it to the list of duplicates
					# or mark that it appeared the first time
					if short_utterance in utterancesDict:
						err = 1
						if jsonPath[intentName][short_utterance]:
							jsonPath[intentName][short_utterance].append(utterance)
						else:
							jsonPath[intentName][short_utterance] = [utterancesDict[short_utterance], utterance]
					else:
						utterancesDict[short_utterance] = utterance

		return err

	def validate(self) -> bool:
		err = self.validateSchema()
		err |= self.validateSlots()
		err |= self.searchDuplicateUtterances()
		return err