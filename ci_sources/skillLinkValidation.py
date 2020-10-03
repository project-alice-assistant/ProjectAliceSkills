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
		'apikey': os.environ['RebrandlyApiKey']
	}
).json()
clicks = [skill['slashtag'].lower() for skill in results]

while clicks:
	skillLinks += clicks
	results = requests.get(
		f"https://api.rebrandly.com/v1/links?last={results[-1]['id']}",
		headers={
			'Content-Type': 'application/json',
			'apikey': os.environ['RebrandlyApiKey']
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


