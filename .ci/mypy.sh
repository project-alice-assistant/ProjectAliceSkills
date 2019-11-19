#!/usr/bin/env bash

ERROR=0
# iterate over all authors in PublishedModules
for author in PublishedModules/*; do
	GREEN='\033[0;32m'
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	echo "${author##*/}"
	# iterate over all modules of an author
	for module in ${author}/*; do
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
		done < <(find "$module" -name "*.py")

		# when no error print success, else print the error output of mypi
		if [ $ERR -eq 0 ]; then
			printf "  ${module##*/}: ${GREEN}Success: no issues found in ${AMOUNT} source file${NC}\n"
		else
			printf "  ${module##*/}: ${RED}${OUTPUT}${NC}\n"
		fi
	done
done
exit $ERROR
