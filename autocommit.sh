#!/bin/bash

git fetch origin

if git log origin/${PUSH_TO} --since="1 minute ago" | egrep . > /dev/null; then
  echo "There's already been a recent commit"
else
  git checkout -f ${PUSH_TO}
  git reset --hard origin/${PUSH_TO}
  git commit --allow-empty -m "$@"
  git push --force origin HEAD:${PUSH_TO}
fi
