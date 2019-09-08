import json

from src.Validation import Validation


class InstallValidation(Validation):

	@property
	def JsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/install-schema.json'
		return json.loads(schema.read_text())


	@property
	def JsonFiles(self) -> list:
		return self._modulePath.glob('*.install')


	def validate(self) -> bool:
		self.validateSchema()
		return self._error
