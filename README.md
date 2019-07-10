[![Build Status](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules.svg?branch=master)](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules)

# ProjectAliceModules

## Testing
You can locally test the Syntax of the dialogTemplates using the dialog-schema, that can be found in [linting/dialog-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/dialog-schema.json). This can be done using ```avj```.
```bash
npm install -g ajv-cli
./linting/dialog-schema.sh 
```
