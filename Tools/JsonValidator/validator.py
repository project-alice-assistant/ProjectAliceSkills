from dialogValidation import dialogValidation
from installValidation import installValidation
from talkValidation import talkValidation
import json
import glob
import os
import sys
from collections import defaultdict
from termcolor import colored

def infinidict():
	return defaultdict(infinidict)

def printMissingSlots(filename: str, errorList: list):
	if errorList:
		print(' ' * 6 + 'missing slots in', filename + ':')
	
	for error in errorList:
		print(' ' * 8 + '-', error)
	if errorList:
		print()

def printDuplicates(filename: str, duplicates: dict):
	if duplicates:
		print(' ' * 6 + 'duplicates in', filename + ':')
	for _, shortUtterances in sorted(duplicates.items()):
		for _, utterances in sorted(shortUtterances.items()):
			for utterance in utterances:
				print(' ' * 8 + '-', utterance)
			print()

def printMissingTypes(filename: str, errorList: list):
	if errorList:
		print(' ' * 6 + 'missing types in', filename + ':')
	
	for error in errorList:
		print(' ' * 8 + '-', error)
	if errorList:
		print()

def printSchemaErrors(filename: str, errorList: list):
	if errorList:
		print(' ' * 6 + 'schema errors in', filename + ':')
	for error in errorList:
		print(' ' * 8 + '-', error)

def printSyntaxError(filename: str, error: str):
	print(' ' * 6 + 'syntax errors in', filename + ':')
	print(' ' * 8 + '-', error)

def printInstaller(error: dict):
	if error == True:
		print(' ' * 4 + colored('Installer', 'white', attrs=['bold']), 'valid')
	else:
		print(' ' * 4 + colored('Installer:', 'white', attrs=['bold']))
		for filename, err in sorted(error['syntax'].items()):
			printSyntaxError(filename, err)

		for filename, err in sorted(error['schema'].items()):
			printSchemaErrors(filename, err)

def printDialog(error: dict):
	if error == True:
		print(' ' * 4 + colored('Dialog files', 'white', attrs=['bold']), 'valid')
	else:
		print(' ' * 4 + colored('Dialog:', 'white', attrs=['bold']))
		for filename, err in sorted(error['syntax'].items()):
			printSyntaxError(filename, err)

		for filename, err in sorted(error['schema'].items()):
			printSchemaErrors(filename, err)

		for filename, err in sorted(error['slots'].items()):
			printMissingSlots(filename, err)

		for filename, types in sorted(error['utterances'].items()):
			printDuplicates(filename, types['duplicates'])

def printTalk(error: dict):
	if error == True:
		print(' ' * 4 + colored('Talk files', 'white', attrs=['bold']), 'valid')
	else:
		print(' ' * 4 + colored('Talk files:', 'white', attrs=['bold']))
		for filename, err in sorted(error['syntax'].items()):
			print(' ' * 6 + 'syntax errors in', filename + ':')
			print(' ' * 8 + '-', err)
		for filename, err in sorted(error['schema'].items()):
			printSchemaErrors(filename, err)

		for filename, err in sorted(error['types'].items()):
			printMissingTypes(filename, err)

dir_path = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.dirname(os.path.dirname(dir_path))
result = infinidict()
err = 0
for module in glob.glob(module_path + '/PublishedModules/*/*'):
	dialog = dialogValidation(module)
	installer = installValidation(module)
	talk = talkValidation(module)
	if dialog.validate():
		err = 1
		result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = dialog.validModules
	else:
		result[dialog.moduleAuthor][dialog.moduleName]['dialogValidation'] = True
	if installer.validate():
		err = 1
		result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = installer.validModules
	else:
		result[installer.moduleAuthor][installer.moduleName]['installerValidation'] = True
	if talk.validate():
		err = 1
		result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = talk.validModules
	else:
		result[talk.moduleAuthor][talk.moduleName]['talkValidation'] = True


for author, _module in sorted(result.items()):
	print(colored('\n{:s}'.format(author), 'green', attrs=['reverse', 'bold']))
	for module, _validate in sorted(_module.items()):
		err = True
		for validate, _valid in sorted(_validate.items()):
			if _valid != True:
				err = False
		print()
		if err:
			print(colored('  {:s}'.format(module), 'green', attrs=['bold']), 'valid')
			continue
		print(colored('  {:s}'.format(module), 'red', attrs=['bold']), 'invalid')
		printInstaller(_validate['installerValidation'])
		printDialog(_validate['dialogValidation'])
		printTalk(_validate['talkValidation'])

sys.exit(err)

