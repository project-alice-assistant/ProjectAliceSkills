import json
from pathlib import Path


class StringCleaner:

	def __init__(self):
		self._modules = Path('../../PublishedModules')
		self._core = Path('../../../ProjectAlice/core')

		self._languageStrings= dict()


	def loadLangFiles(self):
		for p in self._modules.rglob('en.json'):
			if p.parent.stem != 'talks':
				continue
			with p.open() as fp:
				fileContent = json.load(fp)
				d = {key: p.parent for key in fileContent}
				self._languageStrings = {**self._languageStrings, **d}


	def checkLangUsage(self):
		deprecated = dict()
		for key, file in self._languageStrings.items():
			try:
				for p in self._modules.rglob('*.py'):
					with p.open() as fp:
						content = fp.read()
						if f"'{key}'" in content and f'"{key}"' not in content:
							raise Exception

				for p in self._core.rglob('*.py'):
					with p.open() as fp:
						content = fp.read()
						if f"'{key}'" in content and f'"{key}"' not in content:
							raise Exception

				deprecated[key] = file
				print(f'Possible deprecated language string "{key}" in "{file}')
			except:
				continue

		print(f'Found {len(deprecated)} possibly deprecated strings')


if __name__ == '__main__':
	cleaner = StringCleaner()
	cleaner.loadLangFiles()
	cleaner.checkLangUsage()

