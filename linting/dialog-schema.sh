returnCode=0
for file in PublishedModules/*/*/dialogTemplate/*.json
do
  ajv validate -s linting/dialog-schema.json -d $file
  status=$?
  returnCode=$((status||returnCode))
done
[ $returnCode -eq 0 ] || exit 1

