import os
import glob
import json
import re
from src.validation import validation
from src.dialogTemplate import dialogTemplate
from snips_nlu_parsers import get_all_builtin_entities

class dialogValidation(validation):
	
	@property
	def JsonSchema(self) -> dict:
		with open(os.path.join(self.dir_path, 'schemas/dialog-schema.json') ) as json_file:
			return json.load(json_file)
	
	@property
	def JsonFiles(self) -> list:
		return glob.glob( os.path.join(self.modulePath, 'dialogTemplate/*.json') )

	# check whether the slot is a integrated one from snips
	def is_builtin(self, slot: str) -> bool:
		return slot in get_all_builtin_entities()
		
	def installerJsonFiles(self, modulePath: str) -> list:
		return glob.glob( os.path.join(modulePath, '*.install'))


	def searchModule(self, moduleName: str) -> str:
		for module in glob.glob(self.base_path + '/PublishedModules/*/*'):
			if os.path.basename(module) == moduleName:
				return module

	def getRequiredModules(self, modulePath: str = None) -> list:
		if not modulePath:
			modulePath = self.modulePath

		modules = []
		if modulePath not in modules:
			modules.append(modulePath)

		for installer in self.installerJsonFiles(modulePath):
			valid, data = self.validateSyntax(installer)
			if not valid or not 'module' in data['conditions']:
				continue
			for module in data['conditions']['module']:
				if module['name'] != self.moduleName:
					path = self.searchModule(module['name'])
					if path not in modules:
						modules.append(path)
						modules = list(set(modules).union(set(self.getRequiredModules(path))))
		return modules
	
	def getCoreModules(self) -> list:
		return glob.glob(self.base_path + '/PublishedModules/ProjectAlice/*')

	def getAllSlots(self, language: str) -> dict:
		modules = self.getRequiredModules()
		modules = list(set(modules).union(set(self.getCoreModules())))
		all_slots = {}
		for module in modules:
			# get data and check whether it is valid
			path = os.path.join(module, 'dialogTemplate', language)
			if os.path.isfile(path):
				valid, data = self.validateSyntax(path)
				if valid:
					dialog = dialogTemplate(data)
					all_slots.update(dialog.slots)
		return all_slots

	def validateUtteranceSlots(self) -> bool:
		err = 0
		all_slots = {}
		# get slots from all json files of a module
		for file in self.JsonFiles:
			all_slots[file] = self.getAllSlots(os.path.basename(file))

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			jsonPath = self.validModule['utterances'][self.filename(file)]['missingSlots']
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue
			dialog = dialogTemplate(data)
			for intentName, slots in dialog.utteranceSlots.items():
				for slot in slots:
					if not slot in all_slots[file] and not self.is_builtin(slot):
						if intentName in jsonPath:
							jsonPath[intentName].append(slot)
						else:
							jsonPath[intentName] = [slot]
		return err

	def validateSlots(self) -> bool:
		err = 0
		all_slots = {}
		
		# get slots from all json files of a module
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue
			dialog = dialogTemplate(data)
			all_slots.update(dialog.slots)

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue
			dialog = dialogTemplate(data)

			self.validModule['slots'][self.filename(file)] = [k for k, v in all_slots.items() if k not in dialog.slots]
			if self.validModule['slots'][self.filename(file)]:
				err = 1
		return err

	def searchDuplicateUtterances(self) -> bool:
		err = 0
		for file in self.JsonFiles:
			jsonPath = self.validModule['utterances'][self.filename(file)]['duplicates']
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue
			dialog = dialogTemplate(data)
			for intentName, shortUtterances in dialog.shortUtterances.items():
				for shortUtterance, utterances in shortUtterances.items():
					if len(utterances) > 1:
						# Will be added again when duplicates do not improve the performance anymore
						#err = 1
						jsonPath[intentName][shortUtterance] = utterances
			
		return err

	def validate(self) -> bool:
		self.validateUtteranceSlots()
		#print()
		#self.getRequiredModules()
		err = self.validateSchema()
		err |= self.validateSlots()
		err |= self.searchDuplicateUtterances()
		return err