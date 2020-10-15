from __future__ import annotations

from dataclasses import dataclass

import jinja2
import json
import os
import requests
from Version import Version
from git import Repo
from pathlib import Path


@dataclass
class TagVersion:
	skillVersion: Version
	aliceMinVersion: Version


	@classmethod
	def fromString(cls, versionString: str) -> Version:
		skillVersion, aliceMinVersion = str(versionString).split('_')
		return cls(
			Version.fromString(skillVersion),
			Version.fromString(aliceMinVersion))


clickCounts = {}
results = requests.get(
	'https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey'      : os.environ['RebrandlyApiKey']
	}
).json()
clicks = {skill['slashtag']: skill['clicks'] for skill in results}

while clicks:
	clickCounts.update(clicks)
	results = requests.get(
		f"https://api.rebrandly.com/v1/links?last={results[-1]['id']}",
		headers={
			'Content-Type': 'application/json',
			'apikey'      : os.environ['RebrandlyApiKey']
		}
	).json()
	clicks = {skill['slashtag']: skill['clicks'] for skill in results}

skillStore = dict()
skillPath = Path('PublishedSkills')
storePath = Path(__file__).parent.parent.resolve() / 'store'
storePath.mkdir(parents=True, exist_ok=True)

releaseTypes = {
	'a'      : 'alpha',
	'b'      : 'beta',
	'rc'     : 'rc',
	'release': 'master'
}

for releaseType, releaseName in releaseTypes.items():
	for installer in skillPath.glob('*/*.install'):
		skillName = installer.stem
		print(f'{skillName} in {releaseName}')
		try:
			downloads = clickCounts[skillName]
		except KeyError:
			downloads = 0

		templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))
		templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
		template = templateEnv.get_template('badge.tmpl')
		badgeFile = Path(storePath / f'{skillName}.svg')
		badgeFile.write_text(template.render({'downloads': downloads}))

		skillRepo = Repo(installer.parent)
		skillRepo.remote().fetch("--tags")
		tags = [TagVersion.fromString(tag) for tag in skillRepo.tags if '_' in str(tag)]
		tags = [tag for tag in tags if tag.skillVersion.releaseType >= releaseType]
		versions = dict()
		while tags:
			maxVersion = max(tags, key=lambda p: p.skillVersion)
			tags = [tag for tag in tags if tag.aliceMinVersion < maxVersion.aliceMinVersion]
			versions[str(maxVersion.aliceMinVersion)] = str(maxVersion.skillVersion)

		print(f'- Version mapping: {versions}')

		with installer.open() as json_file:
			data = json.load(json_file)
			data['downloads'] = downloads
			data['versionMapping'] = versions

			skillStore[data['name']] = data

	print('Generating samples file')
	samples = dict()
	for sample in skillPath.rglob('*.sample'):
		skillName = sample.parent.parent

		print(f'Found {sample.stem}.sample for skill {skillName.stem}')

		language = sample.stem

		samples = json.loads(sample.read_text())
		samples[str(skillName)] = data

	storeFile = (storePath / f'{releaseName}.json')
	storeFile.write_text(json.dumps(skillStore, ensure_ascii=False, indent=4))

	sampleStoreFile = (storePath / f'{releaseName}.samples')
	sampleStoreFile.write_text(json.dumps(samples, ensure_ascii=False, indent=4))
