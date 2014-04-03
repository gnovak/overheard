import re

def old(aid):
    "Is this an old-style arxiv id?"
    # old-style identifier is seven digits, yymmNNN
    return re.search('^[0-9]{7}(v[0-9]+)?$', aid)

def new(aid):
    "Is this an new-style arxiv id?"
    # new-style identifier is is 4 digits, dot, 4 digits:
    # yymm.NNNN
    return re.search('^[0-9]{4}.[0-9]{4}(v[0-9]+)?$', aid)
 
