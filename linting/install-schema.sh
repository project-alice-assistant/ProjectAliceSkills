for file in PublishedModules/*/*/*.install
do
  ajv validate -s linting/install-schema.json -d $file
  status=$?
  returnCode=$((status||returnCode))
done
[ $returnCode -eq 0 ] || exit 1
