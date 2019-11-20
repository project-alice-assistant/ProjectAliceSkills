import json
from pathlib import Path
from typing import Generator, Optional, Tuple, Union
from unidecode import unidecode

from snips_nlu_parsers import get_all_builtin_entities
from src.DialogTemplate import DialogTemplate
from src.Validation import Validation


class DialogValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/dialog-schema.json'
		return json.loads(schema.read_text())


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._modulePath.glob('dialogTemplate/*.json')


	@staticmethod
	def isSnipsBuiltinSlot(slot: str) -> bool:
		# check whether the slot is a integrated one from snips
		return slot in get_all_builtin_entities()


	#TODO either hard code or retrieve from github
	def isAliceBuiltinSlot(self, slot: str) -> bool:
		#return slot in
		return False


	@staticmethod
	def installerJsonFiles(modulePath: Path) -> Generator[Path, None, None]:
		return modulePath.glob('*.install')


	def searchModule(self, moduleName: str) -> Optional[Path]:
		for module in self._basePath.glob('PublishedModules/*/*'):
			if module.name == moduleName:
				return module
		return None


	# TODO might not exist when validating single module -> get from github
	def getRequiredModules(self, modulePath: Path = None) -> set:
		modulePath = Path(modulePath) if modulePath else self._modulePath
		modules = {modulePath}
		for installer in self.installerJsonFiles(modulePath):
			data = self.validateSyntax(installer)
			if data and 'module' in data['conditions']:
				for module in data['conditions']['module']:
					if module['name'] != modulePath.name:
						path = self.searchModule(module['name'])
						pathSet = {path} if path else set()
						modules = modules.union(pathSet, self.getRequiredModules(path))
		return modules


	# TODO might not exist when validating single module -> get from github
	#def getCoreModules(self) -> Generator[Path, None, None]:
	#	return (self._basePath/'PublishedModules/ProjectAlice').glob('*')


	def getAllSlots(self, language: str) -> dict:
		allSlots = dict()
		for module in self.getRequiredModules():
			# get data and check whether it is valid
			path = module / 'dialogTemplate' / language
			if path.is_file():
				data = self._files[path.stem]
				allSlots.update(DialogTemplate(data).slots)
		return allSlots


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


	def validateIntentSlot(self, allSlots: dict, file: Path, slot: str, values: list, intentName: str) -> Union[list,str]:
		if self.isSnipsBuiltinSlot(slot):
			return
		
		if self.isAliceBuiltinSlot(slot):
			#TODO search if slot value is in there aswell
			return

		if slot in allSlots[file]:
			return self.searchMissingSlotValues(values, allSlots[file][slot])

		return slot

	def validateIntentSlots(self) -> None:
		allSlots = dict()
		# get slots from all json files of a module
		for file in self.jsonFiles:
			allSlots[file] = self.getAllSlots(file.name)

		# check whether the same slots appear in all files
		for file in self.jsonFiles:
			missingSlotValues = dict()
			missingSlots = list()
			data = self._files[file.stem]
			for intentName, slots in DialogTemplate(data).utteranceSlots.items():
				for slot, values in slots.items():
					result = self.validateIntentSlot(allSlots, file, slot, values, intentName)
					if isinstance(result, str):
						missingSlots.append(result)
						self._error = True
					elif result:
						missingSlotValues[slot] = result
						self._error = True
			
			if missingSlots:
				self.indentPrint(2, f'missing slots in {file.parent.name}/{file.name}:')
				self.indentPrint(4, intentName)
				self.printErrorList(missingSlots, 4)
			
			if missingSlotValues:
				self.indentPrint(2, f'missing slot values in {file.parent.name}/{file.name}:')
				for slot, missingValues in sorted(missingSlotValues.items()):
					self.indentPrint(8, f'intent: {intentName}, slot: {slot}')
					self.printErrorList(missingValues, 8)
			
		
	
	def validateIntents(self) -> None:
		allIntents = DialogTemplate(self._files['en']).intents

		# check whether the same intents appear in all files
		for file in self.jsonFiles:

			data = self._files[file.stem]
			missingIntents = [k for k in allIntents if k not in DialogTemplate(data).intents]
			if missingIntents:
				self.indentPrint(2, f'missing intent translation in {file.parent.name}/{file.name}:')
				self.printErrorList(missingIntents, 4)
				self._error = True


	def validateSlots(self) -> None:
		allSlots = DialogTemplate(self._files['en']).slots

		# check whether the same slots appear in all files
		for file in self.jsonFiles:

			data = self._files[file.stem]
			missingSlots = [k for k in allSlots if k not in DialogTemplate(data).slots]
			if missingSlots:
				self.indentPrint(2, f'missing slot translation in {file.parent.name}/{file.name}:')
				self.printErrorList(missingSlots, 4)
				self._error = True


	def searchDuplicateUtterances(self, verbosity: int) -> None:
		for file in self.jsonFiles:
			error = 0
			data = self._files[file.stem]
			for intentName, cleanedUtterances in DialogTemplate(data, verbosity).cleanedUtterances.items():
				for _, utterances in cleanedUtterances.items():
					if len(utterances) > 1:
						if not error:
							error = True
							self.indentPrint(2, f'duplicates in {file.parent.name}/{file.name}:')
						self.indentPrint(4, intentName)
						self.printErrorList(utterances, 4)

			self._error = self._error or error


	def loadFiles(self):
		for file in self.jsonFiles:
			data = self.validateSyntax(file)
			self._files[file.stem] = data

	def validate(self, verbosity: int = 0) -> bool:
		self.loadFiles()
		if self._files['en']:
			self.validateJsonSchemas()
			self.validateSlots()
			self.validateIntents()

			self.searchDuplicateUtterances(verbosity)
			self.validateIntentSlots()
		return self._error
