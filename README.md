[![Build Status](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules.svg?branch=master)](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules)

# ProjectAliceModules

This repository is home of all curated and approved modules for Project Alice.

You can share your own creation as well!

To do so, fork this repository and start adding your modules in a sub directory of **PublishedModules** wearing **your Github username** as directory name. Once your modules tested and working, create a pull request for us to review your module, check it and approve it. Once your module is published it becomes available for everybody to install through the install ticket.


## Testing
The Syntax of the `dialogTemplates` and the `.install` file of all Modules is tested by travis using the [dialog-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/dialog-schema.json) and the [install-schema.json](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/blob/master/linting/install-schema.json). This can be done using [ajv-cli](https://www.npmjs.com/package/ajv-cli). You can run the same tests for the templates locally to check your json files using the following commands:
```bash
npm install -g ajv-cli
./linting/dialog-schema.sh
./linting/install-schema.sh
```
***Be aware, that this only checks the json syntax and not whether the used slots are created in the slotTypes array, or whether the syntax used for the utterances is correct***


## Auto modules creation
Downloading Tools/Moduler you can have a basic tool to create the basic needed files for a module to work. This saves you the hassle of creating the directory tree, the required files and so on. It also follows the strict conventions we made for modules and will avoid you trouble when submitting your module for review.
