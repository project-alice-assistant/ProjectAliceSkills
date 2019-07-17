# ANSI color escape codes
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# get directory this script is placed in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

talk-schema() {
	printf "${BLUE}VALIDATING TALK FILES${NC}\n"

	# validate the all json files using the previously created json schema
	for file in ${DIR/\/Tools\/JsonValidator}/PublishedModules/*/*/talks/*.json
	do
		ajv validate -s $DIR/talk-schema.json -d $file
		returnCode=$(($?||returnCode))
	done

	if [ $returnCode -eq 0 ]; then
		printf "${GREEN}ALL TALK FILES ARE VALID${NC}\n\n"
	else
		printf "${RED}THERE ARE STILL SOME TALK FILES THAT NEEDS SOME LOVE${NC}\n\n"
	fi
	return $returnCode
}

talk-types() {
	printf "${BLUE}VALIDATING WHETHER TALK FILES HAVE CONSISTENT KEYS${NC}\n"

	# iterate over modules (remove Tools/JsonValidator instead of ../.. for better styled output)
	for module in ${DIR/\/Tools\/JsonValidator}/PublishedModules/*/*/talks
	do
		# get language keys
		keys=()
		OLDIFS="$IFS"
		IFS=$'\n'
		for file in $module/*.json
		do
			# no file found so jump to outer loop
			[ $file !=  "$module/*.json" ] || continue 2

			# get keys of the file
			mapfile -t new_keys < <(jq -r 'keys[]' $file)
			# combine current and new keys and remove duplicates
			keys=(`for R in "${keys[@]}" "${new_keys[@]}" ; do echo "$R" ; done | sort -du`)
		done
		IFS="$OLDIFS"

		# validate the all json files using the previously created json schema
		for file in $module/*.json
		do
			# when there is a error, get all missing keys
			mapfile -t new_keys < <(jq -r 'keys[]' $file)
			missing="${keys[*]}"

			for key in ${new_keys[@]}; do
				missing=("${missing[@]/$key}")
			done

			# no keys missing -> continue with next
			[[ -z "${missing// }" ]] && continue

			printf "${GREEN}Missing language keys in %s:${NC}\n" $file
			printf "  - %s\n"  $missing
			returnCode=1
		done
	done

	if [ $returnCode -eq 0 ]; then
		printf "${GREEN}ALL TALK FILES HAVE CONSISTENT TYPES ARE VALID${NC}\n\n"
	else
		printf "${RED}THERE ARE STILL SOME TALK FILES THAT NEEDS SOME LOVE${NC}\n\n"
	fi
	return $returnCode
}

talk() {
	talk-schema
	returnCode=$?
	
	talk-types
	returnCode=$(($?||returnCode))
	
	return $returnCode
}

dialog() {
	printf "${BLUE}VALIDATING DIALOG FILES${NC}\n"

	for file in ${DIR/\/Tools\/JsonValidator}/PublishedModules/*/*/dialogTemplate/*.json
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

	for file in ${DIR/\/Tools\/JsonValidator}/PublishedModules/*/*/*.install
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
	returnCode=$?

	dialog
	returnCode=$(($?||returnCode))

	talk
	returnCode=$(($?||returnCode))

	return $returnCode
}

"$@"
