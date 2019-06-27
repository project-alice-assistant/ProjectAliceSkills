#!/usr/bin/env bash

echo
echo -e "\e[100;33m================================================\e[0m"
echo -e "\e[100;33m            ========================            \e[0m"
echo -e "\e[100;33m                ================                \e[0m"
echo -e "\e[100;33m                    ========                    \e[0m"
echo -e "\e[100;33m                                                \e[0m"
echo -e "\e[100;33m                 Project Alice                  \e[0m"
echo -e "\e[100;33m                    Moduler                     \e[0m"
echo -e "\e[100;33m                                                \e[0m"
echo -e "\e[100;33m                    ========                    \e[0m"
echo -e "\e[100;33m                ================                \e[0m"
echo -e "\e[100;33m            ========================            \e[0m"
echo -e "\e[100;33m================================================\e[0m"
echo

if [[ "$EUID" -ne 0 ]]; then
    echo -e "\e[31mPlease run with sudo\e[0m"
    exit
fi

echo -e "\e[33mHey welcome in this basic module creation tool!\e[0m"
sleep 2

username=''
while [[ ${username} == '' ]]
do
    read -p $'\e[33mPlease type you Github username \e[0m' username
done

moduleName=''
while [[ ${moduleName} == '' ]]
do
    read -p $'\e[33mPlease type the name for the module you are creating \e[0m' moduleName
done

description=''
while [[ ${description} == '' ]]
do
    read -p $'\e[33mPlease type a description for that module \e[0m' description
done

select lang in "en" "fr" "de" "it" "es" "ru" "jp" "kr"
do
	case ${lang} in
	    en|fr|de|it|es|ru|jp|kr)
	        break;;
	    *)
	        echo -e "\e[33mInvalid choice\e[0m"
	esac
done

username=${username^}
moduleName=${moduleName^}

while [[ -d "/home/$(logname)/ProjectAliceModuler/$username/$moduleName" ]]
do
    echo -e "\e[33mThere's already a module named that way...\e[0m"
    read -p $'\e[33mPlease use another name \e[0m' moduleName
done

echo
echo

baseDir=/home/$(logname)/ProjectAliceModuler/${username}/${moduleName}

echo -e "\e[33mCreating base directories...\e[0m"
mkdir -p ${baseDir}/dialogTemplate
mkdir -p ${baseDir}/talks

echo -e "\e[33mCreating install.json\e[0m"
cat > ${baseDir}/install.json << EOL
{
	"name": "${moduleName}",
	"version": "1.0",
	"author": "${username}",
	"maintainers": [],
	"desc": "${description}",
	"aliceMinVersion": "",
	"requirements": [],
	"conditions": {
		"lang": ["${lang}"]
	}
}
EOL

echo -e "\e[33mCreating main class\e[0m"
cat > ${baseDir}/${moduleName}.py << EOL
# -*- coding: utf-8 -*-

import json

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class ${moduleName}(Module):
    """
    Author: ${username}
    Description: ${description}
    """

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
		]

		super(${moduleName}, self).__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		return True
EOL

echo -e "\e[33mCreating download ticket\e[0m"
echo ${username}/${moduleName} > ${baseDir}/${moduleName}

echo -e "\e[33mCreating talks ${lang}.json\e[0m"
cat > ${baseDir}/talks/${lang}.json << EOL
{
	"dummy": {
		"default": [
			"foobar",
			"barfoo"
		],
		"short": [
			"foo",
			"bar"
		]
	},
}
EOL

echo -e "\e[33mCreating dialogTemplate ${lang}.json\e[0m"
cat > ${baseDir}/dialogTemplate/${lang}.json << EOL
{
    "module": "${moduleName}",
    "icon": "time",
    "description": "${description}",
    "slotTypes": [
        {
            "name": "DummySlot",
            "matchingStrictness": null,
            "automaticallyExtensible": false,
            "useSynonyms": true,
            "values": [
                {
                    "value": "foo",
                    "synonyms": ["bar"]
                }
            ]
        }
    ],
    "intents": [
        {
            "name": "Dummy",
            "description": "Do remove this dummy intent!",
            "enabledByDefault": true,
            "utterances": [
                "dummy {foo:=>DummySlotName}",
                "bar"
            ],
            "slots": [
                {
                    "name": "DummySlotName",
                    "description": "dummy",
                    "required": false,
                    "type": "Dummy",
                    "missingQuestion": ""
                }
            ]
        }
    ]
}
EOL

echo -e "\e[33mCreating readme\e[0m"
cat > ${baseDir}/readme.md << EOL
# ${moduleName}

### Desc
${description}

- Version: 1.0
- Author: ${username}
- Alice minimum version: N/A
- Conditions:
  - ${lang}
- Requirements: N/A

EOL

echo
echo -e "\e[33mAll done!\e[0m"
echo -e "\e[33mRemember that all modules shared by the official Project Alice repo must have english!\e[0m"
echo -e "\e[33mYou can now start creating your module. You will find the main class in ${baseDir}/${moduleName}.py\e[0m"
echo
echo -e "\e[33mRemember to edit the dialogTemplate/${lang}.json and remove the dummy data!!\e[0m"
echo
echo -e "\e[33mThank you for creating for Project Alice\e[0m"