[![Build Status](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules.svg?branch=master)](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules)

# ProjectAliceModules

## Testing
The Syntax of the dialogTemplates of all Modules is tested by travis using the dialog-schema, that can be found in [linting/dialog-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/dialog-schema.json). This can be done using [ajv-cli](https://www.npmjs.com/package/ajv-cli). You can run the same tests for the templates locally to check your json files using the following commands:
```bash
npm install -g ajv-cli
./linting/dialog-schema.sh 
```
