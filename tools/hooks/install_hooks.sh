#!/bin/sh
[ ! -d .git ] && echo 'You need to be in your base repo folder where .git is' && exit 1
[ -d .git ] && cp tools/hooks/pre-commit tools/hooks/prepare-commit-msg .git/hooks/ && chmod +x .git/hooks/pre-commit .git/hooks/prepare-commit-msg
echo 'Hooks installed.'
exit 0
