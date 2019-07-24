# -*- coding: utf-8 -*-

import os
import sys
import glob
from jsonschema import Draft7Validator, exceptions
import json
from termcolor import colored
import argparse

dir_path = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.dirname(os.path.dirname(dir_path))
cwd = os.getcwd()

def invalidJSON (schemaPath, filePattern) -> bool:
	with open(schemaPath) as json_file:
		schema = json.load(json_file)

	if Draft7Validator.check_schema(schema):
		sys.stderr.write(colored('{:s} JSON SCHEMA INVALID\n'.format(schemaPath), 'green'))
		return 1

	err = 0
	for file in glob.glob(filePattern):
		with open(file) as json_file:
			data = json.load(json_file)
			try:
				Draft7Validator(schema).validate(data)
				print('{:s} valid'.format(file))
			except exceptions.ValidationError:
				err = 1
				sys.stderr.write(colored('{:s} invalid\n'.format(file), 'green'))
				for error in sorted(Draft7Validator(schema).iter_errors(data), key=str):
					sys.stderr.write('  - {:s}\n'.format(error.message))
				print()
	return err

def install() -> bool:
	print(colored('VALIDATING INSTALLERS', 'blue'))
	err = invalidJSON(dir_path + '/install-schema.json', module_path + '/PublishedModules/*/*/*.install')
	if not err:
		print(colored('ALL INSTALLERS ARE VALID\n\n', 'green'))
	else:
		print(colored('THERE ARE STILL SOME INSTALLERS THAT NEEDS SOME LOVE\n\n', 'red'))
	return err

def dialogSchema() -> bool:
	print(colored('VALIDATING DIALOG FILES', 'blue'))
	err = invalidJSON(dir_path + '/dialog-schema.json', module_path + '/PublishedModules/*/*/dialogTemplate/*.json')
	if not err:
		print(colored('ALL DIALOG FILES ARE VALID\n\n', 'green'))
	else:
		print(colored('THERE ARE STILL SOME DIALOG FILES THAT NEEDS SOME LOVE\n\n', 'red'))
	return err

def dialogSlots() -> bool:
	print(colored('SEARCHING FOR MISSING SLOTS IN DIALOG TEMPLATES', 'blue'))
	err = 0
	for module in glob.glob(module_path + '/PublishedModules/*/*/dialogTemplate'):
		all_slots = {}
		for file in glob.glob(module + '/*.json'):
			with open(file) as json_file:
				jsonDict = json.load(json_file)
                slots = jsonDict['slotTypes']
                for slot in slots:
                    all_slots[slots['name']] = slot

		for file in glob.glob(module + '/*.json'):
			missing = []
			with open(file) as json_file:
				jsonDict = json.load(json_file)
                slots = jsonDict['slotTypes']
                slotDict = []
                for slot in slots:
                    slotDict[slots['name']] = slot

				missing = {k: v for k, v in all_keys.items() if k not in slotDict}

			if not missing.keys():
				print('{:s} valid'.format(file))
			else:
				err = 1
				sys.stderr.write(colored('Missing slots in {:s}:\n'.format(file), 'green'))
				for key in missing.keys():
					sys.stderr.write('  - {:s}\n'.format(key))
				print()

	if not err:
		print(colored('NO MISSING SLOTS\n\n', 'green'))
	else:
		print(colored('THERE ARE STILL SOME MISSING SLOTS\n\n', 'red'))
	return err

def dialog() -> bool:
	err = dialogSchema()
	err |= dialogSlots()
	return err

def talkSchema() -> bool:
	print(colored('VALIDATING TALK FILES', 'blue'))
	err = invalidJSON(dir_path + '/talk-schema.json', module_path + '/PublishedModules/*/*/talks/*.json')
	if not err:
		print(colored('ALL TALK FILES ARE VALID\n\n', 'green'))
	else:
		print(colored('THERE ARE STILL SOME TALK FILES THAT NEEDS SOME LOVE\n\n', 'red'))
	return err

def talkTypes() -> bool:
	print(colored('SEARCHING FOR MISSING LANGUAGE KEYS IN TALK FILES', 'blue'))
	err = 0
	for module in glob.glob(module_path + '/PublishedModules/*/*/talks'):
		all_keys={}
		for file in glob.glob(module + '/*.json'):
			with open(file) as json_file:
				jsonDict = json.load(json_file)
				all_keys = {**all_keys, **jsonDict}

		for file in glob.glob(module + '/*.json'):
			missing = []
			with open(file) as json_file:
				jsonDict = json.load(json_file)
				missing = {k: v for k, v in all_keys.items() if k not in jsonDict}

			if not missing.keys():
				print('{:s} valid'.format(file))
			else:
				err = 1
				sys.stderr.write(colored('Missing language keys in {:s}:\n'.format(file), 'green'))
				for key in missing.keys():
					sys.stderr.write('  - {:s}\n'.format(key))
				print()

	if not err:
		print(colored('NO MISSING LANGUAGE KEYS\n\n', 'green'))
	else:
		print(colored('THERE ARE STILL SOME MISSING LANGUAGE KEYS\n\n', 'red'))
	return err

def talk() -> bool:
	err = talkSchema()
	err |= talkTypes()
	return err

def all() -> bool:
	err = install()
	err |= dialog()
	err |= talk()
	return err

parser = argparse.ArgumentParser(description='decide which files to validate')
parser.add_argument('--all', help='run all validation tasks', action='store_true')
parser.add_argument('--install', help='validate installers', action='store_true')
parser.add_argument('--dialog', help='validate dialog files', action='store_true')
parser.add_argument('--talk', help='validate talk files', action='store_true')


if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args = arguments = parser.parse_args()

if args.all:
    sys.exit(all())

err = 0
if args.install:
	err |= install()
if args.dialog:
	err |= dialog()
if args.talk:
	err |= talk()

sys.exit(err)
