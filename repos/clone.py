#!/usr/bin/env python

import sys
from subprocess import call

filename = sys.argv[1]
f = open(filename, 'r')
i = 0
for line in f:
	if line[0] != '#': # comment syntax
		i = i + 1
		repo = line.rstrip()
		repo_dir = str(i) + "_" + repo.replace(' ', '').replace(':', '_').replace('/', '_')
		call(["git", "clone", repo, repo_dir])
