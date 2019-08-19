import os
import glob
from jsonschema import Draft7Validator, exceptions
import json
from collections import defaultdict
from abc import ABC, abstractmethod

class validation(ABC):
	def __init__(self, modulePath: str):
		self.modulePath = modulePath
		self.validModule = self.infinidict()
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(self.dir_path)))
		self.error = 0

	def infinidict(self):
		return defaultdict(self.infinidict)

	@property
	def validModules(self) -> dict:
		return self.validModule
	
	@property
	@abstractmethod
	def JsonSchema(self) -> dict:
		pass
	
	@property
	@abstractmethod
	def JsonFiles(self) -> list:
		pass

	@property
	def moduleName(self) -> str:
		return os.path.basename(self.modulePath)

	@property
	def moduleAuthor(self) -> str:
		return os.path.split(os.path.split(self.modulePath)[0])[1]

	def filename(self, file: str) -> str:
		return os.path.basename(file)

	def validateSyntax(self, file: str) -> dict:
		data = {}
		try:
			with open(file) as json_file:
				data = json.load(json_file)
		except ValueError as e:
			self.validModule['syntax'][self.filename(file)] = str(e)
			self.error = 1
		return data

	def validateSchema(self) -> None:
		schema = self.JsonSchema
		for file in self.JsonFiles:
			self.validModule['schema'][self.filename(file)] = []
			jsonPath = self.validModule['schema'][self.filename(file)]
			# try to load json from file and return error when the format is invalid
			data = self.validateSyntax(file)
			
			# validate the loaded json
			try:
				Draft7Validator(schema).validate(data)
			except exceptions.ValidationError:
				self.error = 1
				for error in sorted(Draft7Validator(schema).iter_errors(data), key=str):
					jsonPath.append(error.message)

	@abstractmethod
	def validate(self) -> bool:
		pass