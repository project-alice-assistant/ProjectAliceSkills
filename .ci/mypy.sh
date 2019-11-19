#!/usr/bin/env bash

ERROR=0
for author in PublishedModules/*; do
	GREEN='\033[0;32m'
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	echo "${author##*/}"
	for module in ${author}/*; do
		OUTPUT=''
		AMOUNT=0

		while read fname;
		do
  			NEWOUTPUT="$(mypy $fname --pretty)"
			ERR=$?
			AMOUNT=$((AMOUNT+1))
			if [[ $ERR -ne 0 ]]; then
  				OUTPUT="${OUTPUT}\n${NEWOUTPUT}"
				ERROR=$ERR
			fi
		done < <(find $module -name "*.py")

		if [ $ERR -eq 0 ]; then
			printf "  ${module##*/}: ${GREEN}Success: no issues found in ${AMOUNT} source file${NC}\n"
		else
			printf "  ${module##*/}: ${RED}${OUTPUT}${NC}\n"
		fi
	done
done
exit $ERROR
