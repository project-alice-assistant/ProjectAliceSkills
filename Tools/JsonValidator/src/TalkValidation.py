import json
from pathlib import Path
from typing import Generator
import click

from src.Validation import Validation


class TalkValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/talk-schema.json'
		return json.loads(schema.read_text())


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._modulePath.glob('talks/*.json')


	def validateTypes(self):
		# english is the master language
		enSlots = self.validateSyntax(self._modulePath/'talks/en.json')

		# check whether the same slots appear in all files[file.name]
		for file in self.jsonFiles:
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			errors = [k for k, v in enSlots.items() if k not in data]
			if errors:
				self.indentPrint(2, f'missing types in {file.parent.name}/{file.name}:')
				self.printErrorList(errors, 4)
				self._error = True


	def validate(self, verbosity: int = 0) -> bool:
		self.validateJsonSchemas()
		self.validateTypes()
		return self._error
