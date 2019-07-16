# ANSI color escape codes
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# get directory this script is placed in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

talk() {
	talk_schema='{
		"definitions": {
			"talks": {
				"type": "object",
				"required": [
					"default"
				],
				"properties": {
					"default": {
						"type": "array",
						"items": { "type": "string" }
					},
					"short": {
						"type": "array",
						"items": { "type": "string" }
					}
				},
				"additionalProperties": false
			}
		},
		"type": "object",
		"required": [%required_talks%
		],
		"properties": {%talks%
		}
	}'

	printf "${BLUE}VALIDATING TALK FILES${NC}\n"

	# iterate over modules
	for module in $DIR/../../PublishedModules/*/*/talks
	do
		# check if types are specified
		[ -f $module/types.txt ] || continue

		# create json schema for json files
		required_talks=''
		while read p; do
			# ignore lines with comments and empty lines
			if  [[ "$p" != \#* ]] && [[ "$p" != "" ]]
			then
				required_talks="$required_talks\n\t\t\"$p\","
			fi
		done <$module/types.txt

		talks=''
		while read p; do
			# ignore lines with comments and empty lines
			if  [[ "$p" != \#* ]] && [[ "$p" != "" ]]
			then
				talks="$talks\n\t\t\"$p\": { \"\$ref\": \"#/definitions/talks\" },"
			fi
		done <$module/types.txt

		# check if variable is empty
		[ -z "$required_talks" ] && continue
		[ -z "$talks" ] && continue

		# replace placeholders without the trailing ,/talks
		text="${talk_schema/\%required_talks\%/${required_talks::-1}}"
		text="${text/\%talks\%/${talks::-1}}"

		# validate the all json files using the previously created json schema
		for file in $module/*.json
		do
			ajv validate -s <(echo -e "$text") -d $file
			returnCode=$(($?||returnCode))
		done
	done

	if [ $returnCode -eq 0 ]; then
		printf "${GREEN}ALL TALK FILES ARE VALID${NC}\n\n"
	else
		printf "${RED}THERE ARE STILL SOME TALK FILES THAT NEEDS SOME LOVE${NC}\n\n"
	fi
	return $returnCode
}

dialog() {
	printf "${BLUE}VALIDATING DIALOG FILES${NC}\n"

	for file in $DIR/../../PublishedModules/*/*/dialogTemplate/*.json
	do
		ajv validate -s $DIR/dialog-schema.json -d $file
		returnCode=$(($?||returnCode))
	done

	if [ $returnCode -eq 0 ]; then
		printf "${GREEN}ALL DIALOG FILES ARE VALID${NC}\n\n"
	else
		printf "${RED}THERE ARE STILL SOME DIALOG FILES THAT NEEDS SOME LOVE${NC}\n\n"
	fi
	return $returnCode
}

install() {
	printf "${BLUE}VALIDATING INSTALLERS${NC}\n"

	for file in $DIR/../../PublishedModules/*/*/*.install
	do
		ajv validate -s $DIR/install-schema.json -d $file
		returnCode=$(($?||returnCode))
	done

	if [ $returnCode -eq 0 ]; then
		printf "${GREEN}ALL INSTALLERS ARE VALID${NC}\n\n"
	else
		printf "${RED}THERE ARE STILL INSTALLERS THAT NEED SOME LOVE${NC}\n\n"
	fi
	return $returnCode
}

all() {
	printf "${BLUE}STARTING JSON VALIDATION${NC}\n\n"
	install
	returnCode=$(($?||returnCode))

	dialog
	returnCode=$(($?||returnCode))

	talk
	returnCode=$(($?||returnCode))

	return $returnCode
}

"$@"
