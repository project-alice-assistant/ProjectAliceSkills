#  Copyright (c) 2021
#
#  This file, skillLinkValidation.py, is part of Project Alice.
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
#  This file, skillLinkValidation.py, is part of Project Alice.
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
#  Last modified: 2021.04.13 at 12:49:05 CEST

#  This file, skillLinkValidation.py, is part of Project Alice.
#
#
#
#
#  Last modified: 2020/10/3 16:17
#  Last modified by: Psycho

import os
import sys
from pathlib import Path

import click
import requests


skillLinks = []
results = requests.get(
	'https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey'      : os.environ['RebrandlyApiKey']
	}
).json()
clicks = [skill['slashtag'].lower() for skill in results]

while clicks:
	skillLinks += clicks
	results = requests.get(
		f"https://api.rebrandly.com/v1/links?last={results[-1]['id']}",
		headers={
			'Content-Type': 'application/json',
			'apikey'      : os.environ['RebrandlyApiKey']
		}
	).json()
	clicks = [skill['slashtag'].lower() for skill in results]

skillStore = list()
skillPath = Path('PublishedSkills')

err = 0
for installer in skillPath.glob('*/*.install'):
	skillName = installer.stem
	if skillName.lower() not in skillLinks:
		err = 1
		click.secho(f'Install link for {skillName} does not exist yet', fg='red', bold=True)

if not err:
	click.secho(f'All install links exist', fg='green', bold=True)

sys.exit(err)
