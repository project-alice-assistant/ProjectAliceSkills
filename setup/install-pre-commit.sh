#!/bin/sh
# This script installs a pre-commit hook to enforce the correct use of spaces and tabs for this project

GIT_DIR=`git rev-parse --git-common-dir 2> /dev/null`

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
cp $GIT_DIR/../pre-commit.hook $GIT_DIR/hooks/pre-commit

echo
echo "You're all set! Happy hacking!"

exit 0
