#!/usr/bin/env bash

ERROR=0
for author in PublishedModules/*; do
	GREEN='\033[0;32m'
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	echo "${author##*/}"
	for module in ${author}/*; do
		OUTPUT=$(find $module -name '*.py' | xargs mypy --pretty)
		ERR=$?
		if [ $ERR -eq 0 ]; then
			printf "  ${module##*/}: ${GREEN}${OUTPUT}${NC}\n"
		else
			printf "  ${RED}${OUTPUT}${NC}\n"
			ERROR=$ERR
		fi
	done
done
exit $ERROR
