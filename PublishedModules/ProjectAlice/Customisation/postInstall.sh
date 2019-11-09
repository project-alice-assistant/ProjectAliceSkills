#!/usr/bin/env bash

cd ~/ProjectAlice/modules/Customisation || exit

if [[ ! -f "Customisation.py" ]]; then
  mv Customisation.py.dist Customisation.py
fi
