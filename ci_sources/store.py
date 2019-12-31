from pathlib import Path
import jinja2
import requests
import json
import os

clickCounts = requests.get(
	'https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey': os.environ['RebrandlyApiKey']
	}
)

clickCounts = {skill['slashtag']: skill for skill in clickCounts.json()}

skillStore = list()
skillPath = Path('PublishedSkills')
storePath = Path(__file__).parent.parent.resolve() / 'store'
storePath.mkdir(parents=True, exist_ok=True)

for installer in skillPath.glob('*/*/*.install'):
	skillName = installer.stem
	try:
		downloads = clickCounts[skillName]['clicks']
	except KeyError:
		downloads = 0

	templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))
	templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
	template = templateEnv.get_template('badge.tmpl')
	badgeFile = Path(storePath / f'{skillName}.svg')
	badgeFile.write_text(template.render({'downloads': downloads}))

	with installer.open() as json_file:
		data = json.load(json_file)
		data['downloads'] = downloads
		skillStore.append(data)

storeFile = (storePath / 'store.json')
storeFile.write_text(json.dumps(skillStore))
