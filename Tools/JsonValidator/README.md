# JsonValidator

This Tool allows to test the Syntax of the following Alice related JSON files. All the tests are run by travis to validate all the JSON files in the `ProjectAliceModules`
repository aswell. You can run the same tests for the templates locally to check your json files using one of the following commands:
```bash
# run all validation tests
./validation.sh all

# validate dialogTemplates
./validation.sh dialog

# validate talk files
./validation.sh talk

# validate ./install installer files
./validation.sh install
```

## Requirements
This Tool uses [ajv-cli](https://www.npmjs.com/package/ajv-cli) to validate the JSON files using JSON Schemas. It can be installed with the following command:
```bash
npm install -g ajv-cli
```

## dialog Templates

All dialogTemplates have the same JSON Syntax, which is tested using the following JSON Schema [dialog-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/dialog-schema.json).
***Be aware, that currently this only validates, whether the syntax work with Alice, but not whether for example a key is missing in a translated file. This functionality will be added at a later point***

## talk Files

To test your talk files you have to create a file called `types.txt` in your <modulename>/talks directory.
This file is a list of all talk keys, that are required in the corresponding <language>.json files of the module
It is used by the validation script, which makes sure each language file of a module includes all required keys
This is especially helpful when a module has a lot of talk keys, which makes it easy to overlook a newly added key
It is also useful for modules in which the individual languages are developed by different people, so they can check
a lot easier whether they need to translate further texts.

The syntax of this file is a simple list with one key per line. Empty lines and comments and lines starting with
a # are ignored and can be used to structure the keys in groups and add comments.

***Be aware, that when you do not create the `types.txt` file this test will not fail, but it won't run for your module (a file without any keys will be ignored aswell)***

## .install Installer Files
All installer files have the same JSON Syntax, which is tested using the following JSON Schema [install-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/install-schema.json).
