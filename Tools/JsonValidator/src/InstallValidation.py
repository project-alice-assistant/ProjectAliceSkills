import json

from src.Validation import Validation


class InstallValidation(Validation):

	@property
	def jsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/install-schema.json'
		return json.loads(schema.read_text())


	@property
	def jsonFiles(self) -> list:
		return self._modulePath.glob('*.install')


	def validate(self, verbosity: int = 0) -> bool:
		self.validateSchema()
		return self._error
