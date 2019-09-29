import json
from pathlib import Path
from typing import Generator

from src.Validation import Validation


class InstallValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/install-schema.json'
		return json.loads(schema.read_text())


	@property
	def jsonFiles(self) -> Generator[Path, None, None]:
		return self._modulePath.glob('*.install')


	def validate(self, verbosity: int = 0) -> bool:
		self.validateSchema()
		return self._error
