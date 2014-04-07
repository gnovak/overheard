import re

# Would be nice to just or together the two regexps.  However, that
# messes up the group numbers use to pick apart the ids.  Named groups
# seem made to solve this problem, but the re module complains when
# you give two groups the same name, even if they're on exclusive
# branches of an or.

# old-style identifier is archive name followed by seven digits,
# yymmNNN.  archive name is lowercase letters with dashes
old_regexp = '^([-a-z]+)/([0-9]{4})([0-9]{3})(v[0-9]+)?$'

# new-style identifier is is 4 digits, dot, 4 digits:
# yymm.NNNN
new_regexp = '^()([0-9]{4}).([0-9]{4})(v[0-9]+)?$'

# Match fields for both are are section name, yymm, number, version

def old(aid):
    "Is this an old-style arxiv id?"    
    return re.search(old_regexp, aid)

def new(aid):
    "Is this an new-style arxiv id?"
    return re.search(new_regexp, aid)

def archive(aid):
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id!'
    return match.group(1)

def yymm(aid):
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id!'
    return match.group(2)

def number(aid):
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id!'
    return match.group(3)

def version(aid):
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id!'
    # return the empty string rather than None if there's no version
    # specified b/c this makes downstream code simpler.
    return match.group(4) or ''
 
dir_prefix = yymm
