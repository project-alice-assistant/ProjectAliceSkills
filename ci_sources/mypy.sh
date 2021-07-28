#!/usr/bin/env bash

#
# Copyright (c) 2021
#
# This file, mypy.sh, is part of Project Alice.
#
# Project Alice is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
#
# Last modified: 2021.06.25 at 16:43:07 CEST
#

ERROR=0
# iterate over all authors in PublishedSkills
for skill in PublishedSkills/*; do
	GREEN='\033[0;32m'
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	
	OUTPUT=''
	AMOUNT=0

	while read fname; do
		NEWOUTPUT="$(mypy "$fname" --pretty)"
		ERR=$?
		AMOUNT=$((AMOUNT+1))
		# when there is a mypi error append the text from mypi to OUTPUT
		if [[ $ERR -ne 0 ]]; then
			OUTPUT="${OUTPUT}\n${NEWOUTPUT}"
			ERROR=$ERR
		fi
	# use process substitution, so while is not executed in subshell
	done < <(find "$skill" -name "*.py")

	# when no error print success, else print the error output of mypi
	if [ $ERR -eq 0 ]; then
		printf "${skill##*/}: ${GREEN}Success: no issues found in ${AMOUNT} source file${NC}\n"
	else
		printf "${skill##*/}: ${RED}${OUTPUT}${NC}\n"
	fi
done
exit $ERROR
