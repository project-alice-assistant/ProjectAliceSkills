import json
from pathlib import Path
from typing import Generator

from snips_nlu_parsers import get_all_builtin_entities
from src.DialogTemplate import DialogTemplate
from src.Validation import Validation
from unidecode import unidecode


class DialogValidation(Validation):

	@property
	def JsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/dialog-schema.json'
		return json.loads(schema.read_text())


	@property
	def JsonFiles(self) -> list:
		return self._modulePath.glob('dialogTemplate/*.json')


	@staticmethod
	def isBuiltin(slot: str) -> bool:
		# check whether the slot is a integrated one from snips
		return slot in get_all_builtin_entities()


	@staticmethod
	def installerJsonFiles(modulePath: str) -> Generator[Path, None, None]:
		return Path(modulePath).glob('*.install')


	def searchModule(self, moduleName: str) -> Path:
		for module in self._basePath.glob('PublishedModules/*/*'):
			if module.name == moduleName:
				return module


	def getRequiredModules(self, modulePath: Path = None) -> set:
		modulePath = Path(modulePath) if modulePath else self._modulePath
		modules = {modulePath}
		for installer in self.installerJsonFiles(modulePath):
			data = self.validateSyntax(installer)
			if data and 'module' in data['conditions']:
				for module in data['conditions']['module']:
					if module['name'] != self.moduleName:
						path = self.searchModule(module['name'])
						pathSet = {path} if path else set()
						modules = modules.union(pathSet, self.getRequiredModules(path))
		return modules


	def getCoreModules(self) -> list:
		return (self._basePath/'PublishedModules/ProjectAlice').glob('*')


	def getAllSlots(self, language: str) -> dict:
		modules = self.getRequiredModules().union(set(self.getCoreModules()))
		all_slots = {}
		for module in modules:
			# get data and check whether it is valid
			path = module / 'dialogTemplate' / language
			if path.is_file():
				data = self.validateSyntax(path)
				all_slots.update(DialogTemplate(data).slots)
		return all_slots


	@staticmethod
	def searchMissingSlotValues(values: list, allSlots: dict) -> list:
		found = []
		for value in values:
			uValue = unidecode(value).lower()
			for slot in allSlots['values']:
				allValues = [unidecode(slot['value']).lower()]
				if allSlots['useSynonyms'] and 'synonyms' in slot:
					allValues.extend([unidecode(x).lower() for x in slot['synonyms']])

				if uValue in allValues or allSlots['automaticallyExtensible']:
					found.append(value)
		return [x for x in values if x not in found]


	def validateIntentSlots(self) -> None:
		all_slots = {}
		# get slots from all json files of a module
		for file in self.JsonFiles:
			all_slots[file] = self.getAllSlots(file.name)

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			jsonPath = self._validModule['utterances'][file.name]
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			for intentName, slots in DialogTemplate(data).utteranceSlots.items():
				for slot, values in slots.items():
					if not self.isBuiltin(slot):
						if not slot in all_slots[file]:
							self._error = True
							if intentName in jsonPath:
								jsonPath['missingSlots'][intentName].append(slot)
							else:
								jsonPath['missingSlots'][intentName] = [slot]
						else:
							missingValues = self.searchMissingSlotValues(values, all_slots[file][slot])
							if missingValues:
								self._error = True
								jsonPath['missingSlotValue'][intentName][slot] = missingValues


	def validateSlots(self) -> None:
		all_slots = {}
		# get slots from all json files of a module
		for file in self.JsonFiles:
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			all_slots.update(DialogTemplate(data).slots)

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			missingSlots = [k for k in all_slots if k not in DialogTemplate(data).slots]
			self._validModule['slots'][file.name] = missingSlots
			if missingSlots:
				self._error = True


	def searchDuplicateUtterances(self) -> None:
		for file in self.JsonFiles:
			jsonPath = self._validModule['utterances'][file.name]['duplicates']
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			for intentName, shortUtterances in DialogTemplate(data).shortUtterances.items():
				for shortUtterance, utterances in shortUtterances.items():
					if len(utterances) > 1:
						# Will be added again when duplicates do not improve the performance anymore
						# self._error = 1
						jsonPath[intentName][shortUtterance] = utterances


	def validate(self) -> bool:
		self.validateSchema()
		self.validateSlots()
		self.searchDuplicateUtterances()
		self.validateIntentSlots()
		return self._error
