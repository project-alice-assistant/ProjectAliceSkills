#!/usr/bin/env bash

cd "/home/$(logname)/ProjectAlice/modules/Customisation" || exit

if [[ ! -f "Customisation.py" ]]; then
  sudo -u "$(logname)" bash <<EOF
    mv Customisation.py.dist Customisation.py
EOF
fi
