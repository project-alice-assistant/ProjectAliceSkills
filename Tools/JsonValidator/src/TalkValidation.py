import json

from src.Validation import Validation


class TalkValidation(Validation):

	@property
	def JsonSchema(self) -> dict:
		schema = self._dirPath / 'schemas/talk-schema.json'
		return json.loads(schema.read_text())


	@property
	def JsonFiles(self) -> list:
		return self._modulePath.glob('talks/*.json')


	def validateTypes(self) -> bool:
		all_slots = {}
		# get slots from all json files of a module
		for file in self.JsonFiles:
			all_slots.update(self.validateSyntax(file))

		# check whether the same slots appear in all files[file.name]
		for file in self.JsonFiles:
			# get data and check whether it is valid
			data = self.validateSyntax(file)
			self._validModule['types'][file.name] = [k for k, v in all_slots.items() if k not in data]
			if self._validModule['types'][file.name]:
				self._error = True

		return self._error


	def validate(self) -> bool:
		self.validateSchema()
		self.validateTypes()
		return self._error
