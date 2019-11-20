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
		# check whether the same slots appear in all files
		for file in self.jsonFiles:
			errors = [talkType for talkType in self._files['en'] if talkType not in self._files[file.stem]]
			if errors:
				self.saveIndentedError(2, f'missing types in {file.parent.name}/{file.name}:')
				self.printErrorList(errors, 4)
				self._error = True


	def loadFiles(self):
		for file in self.jsonFiles:
			data = self.validateSyntax(file)
			self._files[file.stem] = data


	def validate(self, verbosity: int = 0) -> bool:
		self.loadFiles()
		if self._files['en']:
			self.validateJsonSchemas()
			self.validateTypes()
		return self._error
