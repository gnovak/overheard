import re

# Would be nice to just 'or' together the two regexps.  However, that
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

# Match fields for both are are archive name, yymm, number, version
# 
# For new-style identifiers, the regexp is set up to give the empty
# string for the archive name

def is_old(aid):
    "Is this an old-style arxiv id?"    
    return re.search(old_regexp, aid)

def is_new(aid):
    "Is this an new-style arxiv id?"
    return re.search(new_regexp, aid)

def archive(aid):
    "Extract the archive name from the arxiv id"
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id: %s' % aid
    return match.group(1)

def yymm(aid):
    "Extract the year and month from the arxiv id"
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id: %s' % aid
    return match.group(2)

def number(aid):
    "Extract the serial number from the arxiv id"
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id: %s' % aid
    return match.group(3)

def version(aid):
    "Extract the paper version from the arxiv id"
    match = (re.search(new_regexp, aid) or re.search(old_regexp, aid))
    if not match: raise ValueError, 'Invalid arxiv id: %s' % aid
    # return the empty string rather than None if there's no version
    # specified b/c this makes downstream code simpler.
    return match.group(4) or ''
 
