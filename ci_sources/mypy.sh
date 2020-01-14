#!/usr/bin/env bash

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
