[![Build Status](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules.svg?branch=master)](https://travis-ci.org/project-alice-powered-by-snips/ProjectAliceModules)

# ProjectAliceModules

This repository is home of all curated and approved modules for Project Alice.

You can share your own creation as well!

To do so, fork this repository and start adding your modules in a sub directory of **PublishedModules** wearing **your Github username** as directory name. Once your modules tested and working, create a pull request for us to review your module, check it and approve it. Once your module is published it becomes available for everybody to install through the install ticket.


## Testing
Syntax of `dialogTemplate.json`, `talk.json` and `.install` files of all Modules is tested by travis using json Schemas. Further information on the tests and how to test the files locally can be found in [Tools/JsonValidator](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/tree/master/Tools/JsonValidator).


## Auto modules creation
Downloading Tools/Moduler you can have a basic tool to create the basic needed files for a module to work. This saves you the hassle of creating the directory tree, the required files and so on. It also follows the strict conventions we made for modules and will avoid you trouble when submitting your module for review.
