from pathlib import Path
import requests
import json
import sys
clickCounts = {skill['slashtag']: skill for skill in json.loads(sys.argv[1])}

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

