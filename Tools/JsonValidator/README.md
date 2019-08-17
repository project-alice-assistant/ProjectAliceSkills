# JsonValidator

This Tool allows to test the Syntax of the following Alice related JSON files. All the tests are run by travis to validate all the JSON files in the `ProjectAliceModules`
repository aswell. You can run the same tests for the templates locally to check your json files using one of the following commands:
```bash
# Output all available commands
python3 JsonValidator.py --help

# run all validation tests
python3 JsonValidator.py --all

# validate dialogTemplates
python3 JsonValidator.py --dialog

# validate talk files
python3 JsonValidator.py --talk

# validate ./install installer files
python3 JsonValidator.py --install
```

## Requirements
This Tool uses [jsonschema](https://pypi.org/project/jsonschema/) to validate the JSON files using JSON Schemas and [termcolor](https://pypi.org/project/termcolor/) for a colored output. The requirements can be installed with the following command:
```bash
pip3 install -r requirements.txt
```

## dialog Templates

All dialogTemplates have three validation tests:
1) All dialog Templates have the same JSON Syntax, which is tested using the following JSON Schema [dialog-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/Tools/JsonValidator/dialog-schema.json).
2) The different translations should have the same slots (slotnames). The other settings of the slots like values ect. can be different.
3) There are no duplicates in the utterances. *Duplicates should not improve the performance, but from reports currently still improve it, so this is more of a warning*

***Currently this does not validate whether the utterances are correct, which will be added at a later point***

## talk Files

The talk files have two validation tests:
1) All talk files have the same JSON Syntax, which is tested using the following JSON Schema [talk-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/Tools/JsonValidator/talk-schema.json).
2) The language keys used in the different translations of the talk files are compared to find out whether a language key is missing in one of the files

## .install Installer Files
All installer files have the same JSON Syntax, which is tested using the following JSON Schema [install-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/Tools/JsonValidator/install-schema.json).

