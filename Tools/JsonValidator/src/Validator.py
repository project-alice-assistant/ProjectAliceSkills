from collections import defaultdict
from pathlib import Path
from typing import Optional

import click

from src.DialogValidation import DialogValidation
from src.InstallValidation import InstallValidation
from src.TalkValidation import TalkValidation


class Validator:

	def __init__(self, installer: bool = True, dialog: bool = True, talk: bool = True, verbosity: int = 0):
		self._result = self.infinidict()
		self._dirPath = Path(__file__).resolve().parent.parent
		self._modulePath = self._dirPath.parent.parent
		self._installer = installer
		self._dialog = dialog
		self._talk = talk
		self._verbosity = verbosity


	@staticmethod
	def indentPrint(indent: int, *args):
		click.echo(' ' * (indent - 1) + ' '.join(map(str, args)))


	def infinidict(self):
		return defaultdict(self.infinidict)


	def printMissingSlots(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'missing slot translation in', filename + ':')
			self.printErrorList(errorList, 8)
	

	def printMissingIntents(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'missing intent translation in', filename + ':')
			self.printErrorList(errorList, 8)


	def printDuplicates(self, filename: str, duplicates: dict):
		if duplicates:
			self.indentPrint(6, 'duplicates in', filename + ':')
		for intentName, shortUtterances in sorted(duplicates.items()):
			self.indentPrint(8, intentName)
			for _, utterances in sorted(shortUtterances.items()):
				for utterance in utterances:
					self.indentPrint(8, '-', utterance)
				click.echo()


	def printMissingUtteranceSlots(self, filename: str, errors: dict):
		if errors:
			self.indentPrint(6, 'missing slots in', filename + ':')
		for intentName, missingSlots in sorted(errors.items()):
			self.indentPrint(8, intentName)
			self.printErrorList(missingSlots, 8)


	def printMissingSlotValues(self, filename: str, errors: dict):
		if errors:
			self.indentPrint(6, 'missing slot values in', filename + ':')
		for intentName, slots in sorted(errors.items()):
			for slot, missingValues in sorted(slots.items()):
				self.indentPrint(8, 'intent:', intentName + ', slot:', slot)
				self.printErrorList(missingValues, 8)


	def printMissingTypes(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'missing types in', filename + ':')
			self.printErrorList(errorList, 6)


	def printErrorList(self, errorList: list, indent: int = 0):
		for error in errorList:
			self.indentPrint(indent, '-', error)
		click.echo()


	def printSchemaErrors(self, filename: str, errorList: list):
		if errorList:
			self.indentPrint(6, 'schema errors in', filename + ':')
			self.printErrorList(errorList, 8)


	def printSyntaxError(self, filename: str, error: str):
		self.indentPrint(6, 'syntax errors in', filename + ':')
		self.indentPrint(8, '-', error)


	def printInstaller(self, error: Optional[dict]):
		if not error:
			self.indentPrint(4, click.style('Installer', bold=True), 'valid')
		else:
			self.indentPrint(4, click.style('Installer:', bold=True))
			for filename, err in sorted(error['syntax'].items()):
				self.printSyntaxError(filename, err)

			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)
		click.echo()


	def printDialog(self, error: Optional[dict]):
		if not error:
			self.indentPrint(4, click.style('Dialog files', bold=True), 'valid')
		else:
			self.indentPrint(4, click.style('Dialog files:', bold=True))
			for filename, err in sorted(error['syntax'].items()):
				self.printSyntaxError(filename, err)

			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)
			for filename, err in sorted(error['slots'].items()):
				self.printMissingSlots(filename, err)
			for filename, err in sorted(error['intents'].items()):
				self.printMissingIntents(filename, err)

			for filename, types in sorted(error['utterances'].items()):
				self.printMissingUtteranceSlots(filename, types['missingSlots'])
				self.printMissingSlotValues(filename, types['missingSlotValue'])
				if self._verbosity:
					self.printDuplicates(filename, types['duplicates'])
		click.echo()


	def printTalk(self, error: Optional[dict]):
		if not error:
			self.indentPrint(4, click.style('Talk files', bold=True), 'valid')
		else:
			self.indentPrint(4, click.style('Talk files:', bold=True))
			for filename, err in sorted(error['syntax'].items()):
				self.indentPrint(6, 'syntax errors in', filename + ':')
				self.indentPrint(8, '-', err)
			for filename, err in sorted(error['schema'].items()):
				self.printSchemaErrors(filename, err)

			for filename, err in sorted(error['types'].items()):
				self.printMissingTypes(filename, err)
		click.echo()


	def validate(self):
		err = 0
		for module in self._modulePath.glob('PublishedModules/*/*'):
			dialog = DialogValidation(module)
			installer = InstallValidation(module)
			talk = TalkValidation(module)
			if self._dialog and dialog.validate(self._verbosity):
				err = 1
				self._result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = dialog.validModules
			else:
				self._result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = None
			if self._installer and installer.validate():
				err = 1
				self._result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = installer.validModules
			else:
				self._result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = None
			if self._talk and talk.validate():
				err = 1
				self._result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = talk.validModules
			else:
				self._result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = None
		return err


	def printResult(self):
		for author, _module in sorted(self._result.items()):
			click.secho('\n{}'.format(author), fg='green', reverse=True, bold=True)
			for module, validate in sorted(_module.items()):
				if all(not valid for valid in validate.values()):
					self.indentPrint(2, click.style('{}'.format(module), fg='green', bold=True), 'valid')
					continue
				self.indentPrint(2, click.style('{}'.format(module), fg='red', bold=True), 'invalid')
				if self._installer:
					self.printInstaller(validate['installerValidation'])
				if self._dialog:
					self.printDialog(validate['dialogValidation'])
				if self._talk:
					self.printTalk(validate['talkValidation'])
