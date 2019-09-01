from pathlib import Path
import json
from src.validation import validation

class installValidation(validation):

	@property
	def JsonSchema(self) -> dict:
		schema = self.dir_path / 'schemas/install-schema.json'
		return json.loads(schema.read_text())
	
	@property
	def JsonFiles(self) -> list:
		return self.modulePath.glob('*.install')

	def validate(self) -> bool:
		self.validateSchema()
		return self.error