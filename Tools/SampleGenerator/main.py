#  Copyright (c) 2021
#
#  This file, main.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.07.28 at 16:35:11 CEST

#  Copyright (c) 2021
#
#  This file, main.py, is part of Project Alice.
#
#  Project Alice is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last modified: 2021.04.13 at 12:49:04 CEST

#  This file, main.py, is part of Project Alice.
#
#
#
#
#  Last modified: 2020/10/19 20:10
#  Last modified by: Psycho

import json
from pathlib import Path

import click


skillRoot = Path('../../PublishedSkills/')


@click.group()
def cli():
	"""
	This script generates samples for skill dialogs
	"""
	pass


@cli.command()
def generate():
	for dialogTemplate in skillRoot.rglob('dialogTemplate/*.json'):
		if Path(dialogTemplate.parent, f'{dialogTemplate.stem}.sample').exists():
			continue
		# sample = dict()
		# data = json.loads(dialogTemplate.read_text(encoding='utf-8'))
		# for intent in data['intents']:
		# 	if not intent['enabledByDefault']:
		# 		continue
		# 	sample[intent['name']] = list()

		Path(dialogTemplate.parent, f'{dialogTemplate.stem}.sample').write_text(json.dumps(list(), indent='\t'))
		print(f'Generated samples file for skill {dialogTemplate.parent.parent.stem} in "{dialogTemplate.stem}"')


if __name__ == '__main__':
	cli()
