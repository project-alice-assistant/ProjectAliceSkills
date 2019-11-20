from collections import defaultdict
from pathlib import Path
from typing import Optional

import click

from src.DialogValidation import DialogValidation
from src.InstallValidation import InstallValidation
from src.TalkValidation import TalkValidation
from src.Validation import Validation


class Validator:

	def __init__(self, verbosity: int = 0):
		self._dirPath = Path(__file__).resolve().parent.parent
		self._modulePath = self._dirPath.parent.parent
		self._verbosity = verbosity


	@staticmethod
	def indentPrint(indent: int, *args):
		click.echo(' ' * (indent - 1) + ' '.join(map(str, args)))


	def validate(self):
		err = 0
		for module in self._modulePath.glob('PublishedModules/*/*'):
			dialog = DialogValidation(module)
			installer = InstallValidation(module)
			talk = TalkValidation(module)
			dialog.validate(self._verbosity)
			installer.validate()
			talk.validate()
			
			if dialog.errorCode or installer.errorCode or talk.errorCode:
				err = 1
				self.indentPrint(0, click.style(f'{module.name}', fg='red', bold=True), 'invalid')
				self.printErrors('Installer', installer)
				self.printErrors('Dialog files', dialog)
				self.printErrors('Talk files', talk)
				self.indentPrint(0)
			else:
				self.indentPrint(0, click.style(f'{module.name}', fg='green', bold=True), 'valid')

		return err


	def printErrors(self, name: str, validation: Validation):
		if validation.errorCode:
			self.indentPrint(2, click.style(f'{name}:', bold=True))
			click.echo(validation.errors)
		else:
			self.indentPrint(2, click.style(name, bold=True), 'valid')
