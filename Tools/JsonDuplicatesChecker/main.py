#  Copyright (c) 2021
#
#  This file, main.py, is part of Project Alice.
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
#  Last modified: 2021.07.28 at 16:34:32 CEST

#  Copyright (c) 2021
#
#  This file, main.py, is part of Project Alice.
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

#  This file, main.py, is part of Project Alice.
#
#
#
#
#  Last modified: 2020/9/7 16:45
#  Last modified by: Psycho

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
