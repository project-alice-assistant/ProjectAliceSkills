#!/usr/bin/env bash
#
# Copyright (c) 2021
#
# This file, install-pre-commit.sh, is part of Project Alice.
#
# Project Alice is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
#
# Last modified: 2021.06.25 at 16:43:07 CEST
#

# This script installs a pre-commit hook to enforce the correct use of spaces and tabs for this project

GIT_DIR=$(git rev-parse --git-common-dir 2> /dev/null)

if [ "$GIT_DIR" == "" ]; then
  echo "This does not appear to be a git repo."
  exit 1
fi

if [ -f "$GIT_DIR/hooks/pre-commit" ]; then
  echo "There is already a pre-commit hook installed. Delete it first."
  echo
  echo "    rm '$GIT_DIR/hooks/pre-commit'"
  echo
  exit 2
fi

git config core.whitespace trailing-space,space-before-tab,indent-with-non-tab
cp "$GIT_DIR"/../setup/pre-commit.hook "$GIT_DIR"/hooks/pre-commit

echo
echo "You're all set! Happy hacking!"

exit 0
