from pathlib import Path
import requests
import json
import os


print(os.environ['RebrandlyApiKey'])
clickCounts = requests.get(
	'https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey': os.environ['secrets']['RebrandlyApiKey']
	}
)

clickCounts = {skill['slashtag']: skill for skill in clickCounts.json()}

skillStore = list()
skillPath = Path('PublishedSkills')
for installer in skillPath.glob('*/*/*.install'):
	skillName = installer.stem
	try:
		downloads = clickCounts[skillName]['clicks']
	except KeyError:
		downloads = 0

	with installer.open() as json_file:
		data = json.load(json_file)
		data['downloads'] = downloads
		skillStore.append(data)

storePath = Path('store/store.json')
storePath.parent.mkdir(parents=True, exist_ok=True)
storePath.touch()
storePath.write_text(json.dumps(skillStore))

