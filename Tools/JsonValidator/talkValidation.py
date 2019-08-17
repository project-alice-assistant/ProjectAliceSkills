import os
import glob
import json
from validation import validation

class talkValidation(validation):

	@property
	def JsonSchema(self) -> dict:
		with open(os.path.join(self.dir_path, 'talk-schema.json') ) as json_file:
			return json.load(json_file)
	
	@property
	def JsonFiles(self) -> list:
		return glob.glob( os.path.join(self.modulePath, 'talks/*.json') )

	def validateTypes(self) -> bool:
		err = 0
		all_slots = {}
		
		# get slots from all json files of a module
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue
			all_slots.update(data)

		# check whether the same slots appear in all files
		for file in self.JsonFiles:
			# get data and check whether it is valid
			valid, data = self.validateSyntax(file)
			if not valid:
				err = 1
				continue

			self.validModule['types'][self.filename(file)] = [k for k, v in all_slots.items() if k not in data]
			if self.validModule['types'][self.filename(file)]:
				err = 1
		return err

	def validate(self) -> bool:
		err = self.validateSchema()
		err |= self.validateTypes()
		return err