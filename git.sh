#!/bin/bash
echo What commit label should we use?
read commit

git add git.sh
git add README.md
git add -u
git add *.ipynb
git add *.py
git add *.sh
git commit -m "$commit"
git push https://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@github.com/jonathanqv/camana_semidist.git

