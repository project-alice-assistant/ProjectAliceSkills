import json
from pathlib import Path


class Checker:

	def __init__(self):
		self._baseFile = Path('basejson.json')


	def check(self):
		with self._baseFile.open() as fp:
			theList = json.load(fp)

		newList = list()
		for data in theList['wordlist']:
			if data['value'] in newList:
				print(f'Found a duplicated word: {data["value"]}')
				continue

			newList.append(data['value'])

		print(len(newList))
		print(newList)


if __name__ == '__main__':
	checker = Checker()
	checker.check()
