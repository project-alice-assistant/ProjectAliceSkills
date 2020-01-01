from pathlib import Path
import requests
import click
import json
import os
import sys

clickCounts = requests.get(
	'https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey': os.environ['RebrandlyApiKey']
	}
)

skillLinks = [skill['slashtag'] for skill in clickCounts.json()]

skillStore = list()
skillPath = Path('PublishedSkills')

err = 0
for installer in skillPath.glob('*/*/*.install'):
	skillName = installer.stem
	if skillName not in skillLinks:
		err = 1
		click.secho(f'Install link for {skillName} does not exist yet', fg='red', bold=True)

if not err:
    click.secho(f'All install links exist', fg='green', bold=True)

sys.exit(err)


