import os
import glob
import json
from src.validation import validation

class talkValidation(validation):

	@property
	def JsonSchema(self) -> dict:
		with open(os.path.join(self.dir_path, 'schemas/talk-schema.json') ) as json_file:
			return json.load(json_file)
	
	@property
	def JsonFiles(self) -> list:
		return glob.glob( os.path.join(self.modulePath, 'talks/*.json') )

	def validateTypes(self) -> bool:
		all_slots = {}
		# get slots from all json files of a module
		for file in self.JsonFiles:
			all_slots.update(self.validateSyntax(file))

		# check whether the same slots appear in all files[self.filename(file)]
		for file in self.JsonFiles:
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			self.validModule['types'][self.filename(file)] = [k for k, v in all_slots.items() if k not in data]
			if self.validModule['types'][self.filename(file)]:
				self.error = 1

	def validate(self) -> bool:
		self.validateSchema()
		self.validateTypes()
		return self.error