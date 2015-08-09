#!/usr/bin/env python2
# unfortunately, python3 is not recommended because of 
# Traceback (most recent call last):
#   File "./gffp.py", line 50, in <module>
#     matches_by_time = sorted(find_commits(r, b), key=lambda c: c.committed_date)
#   File "./gffp.py", line 19, in find_commits
#     if b in c.tree.traverse():
#   File "/usr/local/lib/python3.4/dist-packages/gitdb/util.py", line 237, in __getattr__
#     self._set_cache_(attr)
#   File "/usr/local/lib/python3.4/dist-packages/git/objects/commit.py", line 138, in _set_cache_
#     self._deserialize(BytesIO(stream.read()))
#   File "/usr/local/lib/python3.4/dist-packages/git/objects/commit.py", line 448, in _deserialize
#     while next_line.startswith(' '):
# TypeError: startswith first arg must be bytes or a tuple of bytes, not str

import git
import git.repo.fun
import gitdb.exc
import datetime
import sys
import glob
import os

DEBUG = False

# find commits in repository r which contain the blob b
def find_commits(r, b):
	matching_commits = []
	for branch in r.branches:
		for c in ([branch.commit] + list(branch.commit.iter_parents())):
			if DEBUG: print("Checking " + c.name_rev)
			if b in c.tree.traverse():
				matching_commits.append(c)
	return matching_commits

# return a string representation of the committed_date of a commit
def commit_datestr(c):
	return datetime.datetime.utcfromtimestamp(c.committed_date).strftime("%Y-%m-%d %H:%M")

if len(sys.argv) < 3:
	sys.stderr.write("Usage: " + sys.argv[0] + " base-dir-of-git-repos file-to-check [file-to-check2 ...]\n")
	sys.exit(1)

repo_basedir = sys.argv[1]
files        = sys.argv[2:]
abs_files    = list(map((lambda f: os.path.abspath(f)), files))
# use everything that looks like a git repo (has a .git subdir) from repo_basedir
repos        = list(map((lambda d: git.Repo(d)), glob.glob(repo_basedir + "/*/.git")))

if len(repos) < 1:
	sys.stderr.write("No git repositories found below " + repo_basedir + "!\n")
	sys.exit(1)

hashes_to_check = list(map((lambda f: repos[0].git.hash_object(f)), abs_files))

for (f, h) in zip(files, hashes_to_check):
	print("Checking for " + f + " with git hash " + h)
	for r in repos:
		print("  Checking " + r.working_dir)
		try:
			b = git.repo.fun.name_to_object(r, h)
			print("    - found in repo, let's look for commits.")
			matches_by_time = sorted(find_commits(r, b), key=lambda c: c.committed_date)
			latest = matches_by_time[-1]
			first  = matches_by_time[0]
			print("      - first commit: " + first.name_rev + " at " + commit_datestr(first))
			print("      - latest commit: " + latest.name_rev + " at " + commit_datestr(latest))
		except gitdb.exc.BadObject: # does not exist in repo
			pass
