# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

    author: Psycho (Laurent Chervet)
"""

from __future__ import print_function, unicode_literals

try:
	from PyInquirer import style_from_dict, Token, prompt
except ImportError:
	import subprocess
	import time
	subprocess.run(['sudo', 'pip3', 'install', '-r', 'requirements.txt'])
	time.sleep(1)
	from PyInquirer import style_from_dict, Token, prompt

from PyInquirer import Validator, ValidationError

import shutil
import os

style = style_from_dict({
    Token.QuestionMark: '#996633 bold',
    Token.Selected: '#5F819D bold',
    Token.Instruction: '#99ff33 bold',
	Token.Pointer: '#673ab7 bold',
    Token.Answer: '#0066ff bold',
    Token.Question: '#99ff33 bold',
	Token.Input: '#99ff33 bold'
})

class NotEmpty(Validator):
	def validate(self, document):
		ok = len(document.text) > 0
		if not ok:
			raise ValidationError(
				message='This cannot be empty',
				cursor_position=len(document.text)
			)


class NotExist(Validator):
	def validate(self, document):
		ok = len(document.text) > 0 and not os.path.exists(os.path.join(home, 'ProjectAliceModuler', answers['username'], document.text))
		if not ok:
			raise ValidationError(
				message='This cannot be empty and should not already exist',
				cursor_position=len(document.text)
			)

PYTHON_CLASS = '''# -*- coding: utf-8 -*-

import json

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class %moduleName%(Module):
    """
    Author: %username%
    Description: %description%
    """

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
		]

		super(%moduleName%, self).__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		return True'''

INSTALL_JSON = '''{
	"name": "%moduleName%",
	"version": 1.0,
	"author": "%username%",
	"maintainers": [""],
	"desc": "%description%",
	"aliceMinVersion": "",
	"requirements": [%requirements%],
	"conditions": {
		"lang": [%langs%]
	}
}'''

DIALOG_TEMPLATE = '''{
    "module": "%moduleName%",
    "icon": "time",
    "description": "%description%",
    "slotTypes": [
        {
            "name": "DummySlot",
            "matchingStrictness": null,
            "automaticallyExtensible": false,
            "useSynonyms": true,
            "values": [
                {
                    "value": "foo",
                    "synonyms": ["bar"]
                }
            ]
        }
    ],
    "intents": [
        {
            "name": "Dummy",
            "description": "REMOVE this dummy intent!",
            "enabledByDefault": true,
            "utterances": [
                "dummy {foo:=>DummySlotName}",
                "bar"
            ],
            "slots": [
                {
                    "name": "DummySlotName",
                    "description": "dummy",
                    "required": false,
                    "type": "DummySlot",
                    "missingQuestion": ""
                }
            ]
        }
    ]
}'''

TALKS = '''{
	"dummy": {
		"default": [
			"foobar",
			"barfoo"
		],
		"short": [
			"foo",
			"bar"
		]
	},
}'''

README = '''# %moduleName%

### Download
`wget http://bit.ly/????????? -O ~/ProjectAlice/system/moduleInstallTickets/%moduleName%.install`

### Desc
%description%

- Version: 1.0
- Author: %username%
- Maintainers: N/A
- Alice minimum version: N/A
- Conditions:
%langs%
- Requirements: N/A

Configuration
=============

`foo`:
 - type: `bar`
 - desc: `baz`
 
`bar`:
 - type: `baz`
 - desc: `bar`

'''

print()
print('Hey welcome in this basic module creation tool!')

first_questions = [
	{
		'type'    : 'input',
		'name'    : 'username',
		'message' : 'Please enter your Github user name',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize().replace(' ', '')
	},
	{
		'type'    : 'input',
		'name'    : 'moduleName',
		'message' : 'Please enter the name of the module you are creating',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize().replace(' ', '')
	}
]

next_questions = [
	{
		'type'    : 'input',
		'name'    : 'description',
		'message' : 'Please enter a description for this module',
		'validate': NotEmpty,
		'filter'  : lambda val: str(val).capitalize()
	},
	{
		'type'    : 'checkbox',
		'name'    : 'langs',
		'message' : 'Choose the language for this module. Note that to share\nyour module on the official repo english is mendatory',
		'validate': NotEmpty,
		'choices': [
			{
				'name': 'en',
				'checked': True
			},
			{
				'name': 'fr'
			},
			{
				'name': 'de'
			},
			{
				'name': 'es'
			},
			{
				'name': 'it'
			},
			{
				'name': 'jp'
			},
			{
				'name': 'kr'
			},
		]
	}
]

if __name__ == '__main__':
	home = os.path.expanduser('~')
	answers = prompt(first_questions, style=style)

	modulePath = os.path.join(home, 'ProjectAliceModuler', answers['username'], answers['moduleName'])

	while os.path.exists(modulePath):
		questions = [
			{
				'type'    : 'confirm',
				'name'    : 'delete',
				'message' : 'Seems like this module name already exists.\nDo you want to delete it locally?',
				'default' : False
			},
			{
				'type'    : 'input',
				'name'    : 'moduleName',
				'message' : 'Ok, so chose another module name please',
				'validate': NotEmpty,
				'filter'  : lambda val: str(val).capitalize().replace(' ', ''),
				'when'    : lambda subAnswers: not subAnswers['delete']
			}
		]
		subAnswers = prompt(questions, style=style)
		if subAnswers['delete']:
			shutil.rmtree(path = modulePath)
		else:
			modulePath = os.path.join(home, 'ProjectAliceModuler', answers['username'], subAnswers['moduleName'])
			answers['moduleName'] = subAnswers['moduleName']

	subAnswers = prompt(next_questions, style = style)
	answers = {**answers, **subAnswers}

	reqs = []
	while True:
		questions = [
			{
				'type'   : 'confirm',
				'name'   : 'requirements',
				'message': 'Do you want to add python requirements?',
				'default': False
			},
			{
				'type'    : 'input',
				'name'    : 'req',
				'message' : 'Enter the pip requirement name or `stop` to cancel',
				'validate': NotEmpty,
				'when'    : lambda subAnswers: subAnswers['requirements']
			}
		]
		subAnswers = prompt(questions, style=style)
		if subAnswers['requirements'] and subAnswers['req'] != 'stop':
			reqs.append(subAnswers['req'])
		else:
			break

	print()
	print('----------------------------')
	print('Creating destination folders')

	os.makedirs(modulePath)
	os.mkdir(os.path.join(modulePath, 'dialogTemplate'))
	os.mkdir(os.path.join(modulePath, 'talks'))

	print('Creating python class')
	with open(os.path.join(modulePath, answers['moduleName'] + '.py'), 'w') as f:
		f.write(PYTHON_CLASS.replace('%moduleName%', answers['moduleName']).replace('%description%', answers['description']).replace('%username%', answers['username']))

	print('Creating install file')
	with open(os.path.join(modulePath, answers['moduleName'] + '.install'), 'w') as f:
		langs = ''
		for lang in answers['langs']:
			langs += '"{}", '.format(lang)

		requirements = ''
		if reqs:
			for req in reqs:
				requirements += '"{}", '.format(req)

		f.write(INSTALL_JSON.replace('%moduleName%', answers['moduleName'])
							.replace('%description%', answers['description'])
							.replace('%username%', answers['username'])
							.replace('%langs%', langs[:-2])
							.replace('%requirements%', requirements[:-2])
		)

	print('Creating dialog template(s)')
	for lang in answers['langs']:
		print('- {}'.format(lang))
		with open(os.path.join(modulePath, 'dialogTemplate', lang + '.json'), 'w') as f:
			f.write(DIALOG_TEMPLATE.replace('%moduleName%', answers['moduleName'])
								   .replace('%description%', answers['description'])
								   .replace('%username%', answers['username'])
					)

	print('Creating talks')
	for lang in answers['langs']:
		print('- {}'.format(lang))
		with open(os.path.join(modulePath, 'talks', lang + '.json'), 'w') as f:
			f.write(TALKS.replace('%moduleName%', answers['moduleName']))

	print('Creating readme file')
	with open(os.path.join(modulePath, 'readme.md'), 'w') as f:
		langs = ''
		for lang in answers['langs']:
			langs += '  - {}\n'.format(lang)

		f.write(README.replace('%moduleName%', answers['moduleName'])
					  .replace('%description%', answers['description'])
					  .replace('%username%', answers['username'])
					  .replace('%langs%', langs[:-2])
		)

	print('----------------------------')
	print()
	print('All done!')
	print('You can now start creating your module. You will find the main class in {}/{}.py'.format(modulePath, answers['moduleName']))
	print()
	print('Remember to edit the dialogTemplate/${lang}.json and remove the dummy data!!')
	print()
	print('Thank you for creating for Project Alice')