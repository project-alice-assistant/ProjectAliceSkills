#  Copyright (c) 2021
#
#  This file, store.py, is part of Project Alice.
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
#  This file, store.py, is part of Project Alice.
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

#  This file, store.py, is part of Project Alice.
#
#
#
#
#  Last modified: 2021/2/23 20:34
#  Last modified by: Psycho

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import requests
from git import Repo

from Version import Version


@dataclass
class TagVersion:
	skillVersion: Version
	aliceMinVersion: Version


	@classmethod
	def fromString(cls, versionString: str) -> TagVersion:
		skillVersion, aliceMinVersion = str(versionString).split('_')
		return cls(Version.fromString(skillVersion), Version.fromString(aliceMinVersion))


clickCounts = dict()
results = requests.get(
	url='https://api.rebrandly.com/v1/links',
	headers={
		'Content-Type': 'application/json',
		'apikey'      : os.environ['RebrandlyApiKey']
	}
).json()

clicks = {skill['slashtag']: skill['clicks'] for skill in results}

while clicks:
	clickCounts.update(clicks)
	results = requests.get(
		url=f"https://api.rebrandly.com/v1/links?last={results[-1]['id']}",
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

for installer in skillPath.glob('*/*.install'):
	skillName = installer.stem
	print(f'Building for "{skillName}"')

	skillRepo = Repo(installer.parent)
	skillRepo.remote().fetch('--tags')
	tags = [TagVersion.fromString(tag) for tag in skillRepo.tags if '_' in str(tag)]

	versions = dict()
	while tags:
		maxVersion = max(tags, key=lambda p: p.skillVersion)
		tags = [tag for tag in tags if tag.aliceMinVersion < maxVersion.aliceMinVersion]
		versions[str(maxVersion.aliceMinVersion)] = str(maxVersion.skillVersion)

	print(f'- Version mapping: {versions}')

	try:
		downloads = clickCounts[skillName]
	except KeyError:
		downloads = 0

	with installer.open() as json_file:
		data = json.load(json_file)
		data['downloads'] = downloads
		data['versionMapping'] = versions
		skillStore[data['name']] = data

print('Generating samples file')
samples = dict()
for sample in skillPath.rglob('*.sample'):
	skillName = sample.parent.parent.stem
	print(f'Found {sample.stem}.sample for skill {skillName}')
	language = sample.stem
	try:
		intentsSamples = json.loads(sample.read_text())
		samples.setdefault(str(skillName), dict())
		samples[str(skillName)][language] = intentsSamples
	except:
		print('Invalid sample file, skip')

storeFile = (storePath / f'skills.json')
storeFile.write_text(json.dumps(skillStore, ensure_ascii=False, indent='\t', sort_keys=True))

sampleStoreFile = (storePath / f'skills.samples')
sampleStoreFile.write_text(json.dumps(samples, ensure_ascii=False, indent='\t', sort_keys=True))
