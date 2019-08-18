from src.dialogValidation import dialogValidation
from src.installValidation import installValidation
from src.talkValidation import talkValidation
import json
import glob
import os
from collections import defaultdict
from termcolor import colored

class validator:
	def __init__(self, installer: bool = True, dialog: bool = True, talk: bool = True):
		self.result = self.infinidict()
		self.dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
		self.module_path = os.path.dirname(os.path.dirname(self.dir_path))
		self.installer = installer
		self.dialog = dialog
		self.talk = talk

	def indentPrint(self, indent: int, *args: tuple):
		text = ' ' * (indent-1) + ' '.join(map(str, args))
		print(text)
	
	def infinidict(self):
		return defaultdict(self.infinidict)
	
	def printMissingSlots(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'missing slots in', filename + ':')
		
		self.printErrorList(errorList, 8)
		if errorList:
			print()
	
	def printDuplicates(self, filename: str, duplicates: dict):
		if duplicates:
			self.indentPrint(6, 'duplicates in', filename + ':')
		for _, shortUtterances in sorted(duplicates.items()):
			for _, utterances in sorted(shortUtterances.items()):
				for utterance in utterances:
					self.indentPrint(8, '-', utterance)
				print()
	
	def printMissingTypes(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'missing types in', filename + ':')
		self.printErrorList(errorList, 8)
		if errorList:
			print()
	
	def printErrorList(self, errorList: list, indent: int = 0):
		for error in errorList:
			self.indentPrint(indent, '-', error)
	
	def printSchemaErrors(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'schema errors in', filename + ':')
		self.printErrorList(errorList, 8)
	
	def printSyntaxError(self, filename: str, error: str):
		self.indentPrint(6, 'syntax errors in', filename + ':')
		self.indentPrint(8, '-', error)
	
	def printInstaller(self, error: dict):
		if error == True:
			self.indentPrint(4, colored('Installer', 'white', attrs=['bold']), 'valid')
		else:
			self.indentPrint(4, colored('Installer:', 'white', attrs=['bold']))
			for filename, err in sorted(error['syntax'].items()):
				self.printSyntaxError(filename, err)
	
			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)
	
	def printDialog(self, error: dict):
		if error == True:
			self.indentPrint(4, colored('Dialog files', 'white', attrs=['bold']), 'valid')
		else:
			self.indentPrint(4, colored('Dialog files:', 'white', attrs=['bold']))
			for filename, err in sorted(error['syntax'].items()):
				self.printSyntaxError(filename, err)
	
			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)
	
			for filename, err in sorted(error['slots'].items()):
				self.printMissingSlots(filename, err)
	
			for filename, types in sorted(error['utterances'].items()):
				self.printDuplicates(filename, types['duplicates'])
	
	def printTalk(self, error: dict):
		if error == True:
			self.indentPrint(4, colored('Talk files', 'white', attrs=['bold']), 'valid')
		else:
			self.indentPrint(4, colored('Talk files:', 'white', attrs=['bold']))
			for filename, err in sorted(error['syntax'].items()):
				self.indentPrint(6, 'syntax errors in', filename + ':')
				self.indentPrint(8, '-', err)
			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)
	
			for filename, err in sorted(error['types'].items()):
				self.printMissingTypes(filename, err)
	

	def validate(self):
		err = 0
		for module in glob.glob(self.module_path + '/PublishedModules/*/*'):
			dialog = dialogValidation(module)
			installer = installValidation(module)
			talk = talkValidation(module)
			if self.dialog and dialog.validate():
				err = 1
				self.result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = dialog.validModules
			else:
				self.result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = True
			if self.installer and installer.validate():
				err = 1
				self.result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = installer.validModules
			else:
				self.result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = True
			if self.talk and talk.validate():
				err = 1
				self.result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = talk.validModules
			else:
				self.result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = True

		return err
	
	def printResult(self):
		for author, _module in sorted(self.result.items()):
			print(colored('\n{:s}'.format(author), 'green', attrs=['reverse', 'bold']))
			for module, _validate in sorted(_module.items()):
				err = True
				for validate, _valid in sorted(_validate.items()):
					if _valid != True:
						err = False
				print()
				if err:
					self.indentPrint(2, colored('{:s}'.format(module), 'green', attrs=['bold']), 'valid')
					continue
				self.indentPrint(2, colored('{:s}'.format(module), 'red', attrs=['bold']), 'invalid')
				if self.installer:
					self.printInstaller(_validate['installerValidation'])
				if self.dialog:
					self.printDialog(_validate['dialogValidation'])
				if self.talk:
					self.printTalk(_validate['talkValidation'])

