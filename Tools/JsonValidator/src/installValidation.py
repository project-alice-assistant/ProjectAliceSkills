import os
import glob
import json
from src.validation import validation

class installValidation(validation):

	@property
	def JsonSchema(self) -> dict:
		with open(os.path.join(self.dir_path, 'schemas/install-schema.json') ) as json_file:
			return json.load(json_file)
	
	@property
	def JsonFiles(self) -> list:
		return glob.glob( os.path.join(self.modulePath, '*.install') )

	def validate(self) -> bool:
		self.validateSchema()
		return self.error