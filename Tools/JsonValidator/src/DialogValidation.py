import json
from pathlib import Path
from typing import Generator, Optional, Tuple, Union
from unidecode import unidecode
import requests

from snips_nlu_parsers import get_all_builtin_entities
from src.DialogTemplate import DialogTemplate
from src.Validation import Validation


class DialogValidation(Validation):

	def __init__(self, username: str = None, token: str = None):
		self._coreDialogTemplates = dict()
		self._branch = 'master'
		super().__init__(username, token)


	def getCoreModules(self, language: str):
		# only load language once
		if language in self._coreDialogTemplates:
			return

		self._coreDialogTemplates[language] = list()
		url = f'https://api.github.com/repositories/193512918/contents/PublishedModules/ProjectAlice?ref={self._branch}'
		modulesRequest = requests.get(url, auth=self._githubAuth)
		modulesRequest.raise_for_status()
		modules = modulesRequest.json()
		for module in modules:
			try:
				moduleName = module['name']
				url = f'https://raw.githubusercontent.com/project-alice-powered-by-snips/ProjectAliceModules/{self._branch}/PublishedModules/ProjectAlice/{moduleName}/dialogTemplate/{language}.json'
				moduleRequest = requests.get(url, auth=self._githubAuth)
				moduleRequest.raise_for_status()
				self._coreDialogTemplates[language].append(moduleRequest.json())
			# TODO use better exceptions
			except Exception:
				continue


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


	@staticmethod
	def installerJsonFiles(modulePath: Path) -> Generator[Path, None, None]:
		return modulePath.glob('*.install')


	def searchModule(self, moduleName: str) -> Optional[Path]:
		for module in self._basePath.glob('PublishedModules/*/*'):
			if module.name == moduleName:
				return module
		return None


	def getRequiredModules(self, modulePath: Path = None) -> set:
		modulePath = Path(modulePath) if modulePath else self._modulePath
		modules = {modulePath}
		# TODO get from github same for .install files
		#for installer in self.installerJsonFiles(modulePath):
		#	data = self.validateSyntax(installer)
		#	if data and 'module' in data['conditions']:
		#		for module in data['conditions']['module']:
		#			if module['name'] != modulePath.name:
		#				path = self.searchModule(module['name'])
		#				pathSet = {path} if path else set()
		#				modules = modules.union(pathSet, self.getRequiredModules(path))
		return modules



	def getAllSlots(self, language: str) -> dict:
		allSlots = dict()
		try:
			self.getCoreModules(language)
		# TODO use better exceptions
		except Exception:
			pass

		for dialogTemplate in self._coreDialogTemplates[language]:
			allSlots.update(DialogTemplate(dialogTemplate).slots)

		for module in self.getRequiredModules():
			path = module / 'dialogTemplate' / f'{language}.json'
			if path.is_file():
				data = self._files[path.stem]
				allSlots.update(DialogTemplate(data).slots)
		return allSlots


	@staticmethod
	def searchMissingSlotValues(values: list, slot: dict) -> list:
		if slot['automaticallyExtensible']:
			return list()

		allValues = list()
		for slotValue in slot['values']:
			allValues.append(unidecode(slotValue['value']).lower())
			allValues.extend([unidecode(x).lower() for x in slotValue.get('synonyms', list())])

		return [value for value in values if unidecode(value).lower() not in allValues]


	def validateIntentSlot(self, language: str, slot: str, values: list) -> Union[list,str]:
		if self.isSnipsBuiltinSlot(slot):
			return

		allSlots = self.getAllSlots(language)
		if slot in allSlots:
			return self.searchMissingSlotValues(values, allSlots[slot])

		return slot


	def validateIntentSlots(self) -> None:
		for file in self.jsonFiles:
			missingSlotValues = dict()
			missingSlots = list()
			data = self._files[file.stem]
			for intentName, slots in DialogTemplate(data).utteranceSlots.items():
				for slot, values in slots.items():
					result = self.validateIntentSlot(file.stem, slot, values)
					if isinstance(result, str):
						missingSlots.append(result)
						self._error = True
					elif result:
						missingSlotValues[slot] = result
						self._error = True
			
			if missingSlots:
				self.saveIndentedError(2, f'missing slots in {file.parent.name}/{file.name}:')
				self.saveIndentedError(4, intentName)
				self.printErrorList(missingSlots, 4)
			
			if missingSlotValues:
				self.saveIndentedError(2, f'missing slot values in {file.parent.name}/{file.name}:')
				for slot, missingValues in sorted(missingSlotValues.items()):
					self.saveIndentedError(8, f'intent: {intentName}, slot: {slot}')
					self.printErrorList(missingValues, 8)
			
		
	
	def validateIntents(self) -> None:
		allIntents = DialogTemplate(self._files['en']).intents

		# check whether the same intents appear in all files
		for file in self.jsonFiles:

			data = self._files[file.stem]
			missingIntents = [k for k in allIntents if k not in DialogTemplate(data).intents]
			if missingIntents:
				self.saveIndentedError(2, f'missing intent translation in {file.parent.name}/{file.name}:')
				self.printErrorList(missingIntents, 4)
				self._error = True


	def validateSlots(self) -> None:
		allSlots = DialogTemplate(self._files['en']).slots

		# check whether the same slots appear in all files
		for file in self.jsonFiles:
			data = self._files[file.stem]
			missingSlots = [k for k in allSlots if k not in DialogTemplate(data).slots]
			if missingSlots:
				self.saveIndentedError(2, f'missing slot translation in {file.parent.name}/{file.name}:')
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
							self.saveIndentedError(2, f'duplicates in {file.parent.name}/{file.name}:')
						self.saveIndentedError(4, intentName)
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
