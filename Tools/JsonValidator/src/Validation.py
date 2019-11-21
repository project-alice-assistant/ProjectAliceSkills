import json
from pathlib import Path
from typing import Generator
import click

from abc import ABC, abstractmethod
from jsonschema import Draft7Validator, exceptions


class Validation(ABC):

	def __init__(self, username: str = None, token: str = None):
		self._modulePath = None
		self._dirPath = Path(__file__).resolve().parent
		self._basePath = self._dirPath.parent.parent.parent
		self._error = False
		self._files = dict()
		self.errors = ''
		self._githubAuth = (username, token) if (username and token) else None


	def reset(self, modulePath: Path):
		self._modulePath = modulePath
		self._error = False
		self.errors = ''


	@property
	def errorCode(self) -> bool:
		return self._error


	def saveIndentedError(self, indent: int, *args):
		self.errors += ' ' * indent + ' '.join(map(str, args)) + '\n'


	@property
	@abstractmethod
	def jsonSchema(self) -> dict:
		pass


	@property
	@abstractmethod
	def jsonFiles(self) -> Generator[Path, None, None]:
		pass


	def validateSyntax(self, file: Path) -> dict:
		data: dict = dict()
		try:
			data = json.loads(file.read_text())
		except ValueError as e:
			self.saveIndentedError(2, f'syntax errors in {file.parent.name}/{file.name}:')
			self.saveIndentedError(4, f'- {e}')
			self._error = True
		except FileNotFoundError:
			self.saveIndentedError(2, f'Required file {file.parent.name}/{file.name} not found')
			self._error = True

		return data


	def printErrorList(self, errorList: list, indent: int = 0):
		if errorList:
			for error in errorList:
				self.saveIndentedError(indent, '-', error)
			self.saveIndentedError(0)


	def validateJsonSchema(self, file: Path):
		schema = self.jsonSchema
		data = self.validateSyntax(file)
		errors = list()
		try:
			Draft7Validator(schema).validate(data)
		except exceptions.ValidationError:
			self._error = True
			for error in sorted(Draft7Validator(schema).iter_errors(data), key=str):
				errors.append(error.message)

		if errors:
			self.saveIndentedError(2, f'schema errors in {file.parent.name}/{file.name}:')
			self.printErrorList(errors, 4)


	def validateJsonSchemas(self):
		for file in self.jsonFiles:
			self.validateJsonSchema(file)


	@abstractmethod
	def validate(self, verbosity: int = 0) -> bool:
		pass
