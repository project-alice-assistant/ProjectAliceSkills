[![Modules Valid](https://github.com/project-alice-assistant/ProjectAliceModules/workflows/Modules%20Validation/badge.svg)](https://github.com/project-alice-assistant/ProjectAliceModules/actions)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8c37d708cde34cb998b45ff5d6e92d43)](https://www.codacy.com/manual/ProjectAlice/ProjectAliceModules?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=project-alice-powered-by-snips/ProjectAliceModules&amp;utm_campaign=Badge_Grade)
![GitHub](https://img.shields.io/github/license/Psychokiller1888/ProjectAliceModules)
[![Maintainability](https://api.codeclimate.com/v1/badges/1c61965accf480b5d5ef/maintainability)](https://codeclimate.com/github/project-alice-powered-by-snips/ProjectAliceModules/maintainability)

# ProjectAliceModules (alpha3)

This repository is home of all curated and approved modules for Project Alice.

You can share your own creation as well!

To do so, fork this repository and start adding your modules in a sub directory of **PublishedModules** wearing **your Github username** as directory name. Once your modules tested and working, create a pull request for us to review your module, check it and approve it. Once your module is published it becomes available for everybody to install through the install ticket.


## Testing
Syntax of `dialogTemplate.json`, `talk.json` and `Module.install` files of all Modules is tested with github actions using json Schemas.
To test a Module locally use [alice-sk](https://github.com/project-alice-powered-by-snips/ProjectAliceSkillKit)
```
pip3 install alice-sk
alice-sk validate --paths <list of paths of modules to test>
```


## Auto modules creation
Downloading Tools/Moduler you can have a basic tool to create the basic needed files for a module to work. This saves you the hassle of creating the directory tree, the required files and so on. It also follows the strict conventions we made for modules and will avoid you trouble when submitting your module for review.


## Copyright
Project Alice ships under GPLv3, it means you are free to use and redistribute our code but are not allowed to use any part of it under a closed license. Give the community back what you've been given!
Regarding third party tools, scripts, material we use, I took care to mention original creators in files and respect their copyright. If something has slept under my supervision know that it was in no case intended and is the result of a mistake and I ask you to contact me directly to solve the issue asap.
By submitting your work to this repository you agree to share your code with us under the same terms and accept that the community is free to reuse it by keeping your in file credits untouched.
