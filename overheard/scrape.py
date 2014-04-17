#########
# Notes #
#########
# 
# When scraping comments out of tex files, separate short comments
# (less than full line) from long comments (at least one full line)
# because the character of what is said is typically different in a
# few words vs. a full paragraph.
# 
# Comments: Backslash-percent (to get percent into the latex output)
# shows up in the python strings as "\\%" and a regexp for just '%'
# doesn't match them, which simplifies my life...

from __future__ import with_statement

import os, re

import fetch, util

verbose = True

# long comment is 'optional whitepace % comment'
long_comment_regexp = "^\s*(%.*)$"

# Short comment is "string including at least one non-whitespace char
# and not including percent, percent, any string."  
# 
# Can't find a regexp that matches 'some % comment % and more' but not
# ' % comment $ and more' which is a long comment.  Therefore define a
# short comment to be "some string + longest string starting with
# percent, that doesn't also match long_comment_regexp"
short_comment_regexp = '.*?(%.*)$'

encodings = ['utf-8',
             'latin-1',
             'GB2312',
             'Windows-1251',
             'Windows-1252',
             'utf-16',
             'utf-32',
             'ucs-1',
             'ucs-2',
             'ucs-4']

def readlines(fn):
    """Read all lines from fn

    Loop over guesses at the text encoding.

    Can/should be more intelligent about this + read first big of file
    to see if encoding is specified.

    """
    lines = None
    error = None
    for enc in encodings:
        try:
            with open(fn, encoding=enc) as ff:
                lines = ff.readlines()
        except UnicodeDecodeError, exc:
            error = exc
            continue
        # Making it here means there were no errors on read.  Accept
        # the encoding and continue
        return lines
    # This means no encodings were successful, raise exception
    if lines is None:
        raise error

def long_comments(aid):
    "Scrape full-line and multi-line comments out of latex file"
    lines = readlines(fetch.latex_file_path(aid))
    return long_comments_from_lines(lines)

def long_comments_from_lines(lines):
    "Get long comments out of latex file"

    # State variable
    comment_started = False 
    # Contains current comment
    comment = []
    # Contains list of all comments -- overall output
    result = []

    for line in lines:
        line_is_comment = re.search(long_comment_regexp, line)
        if not comment_started and line_is_comment:
            # beginning of comment
            comment = [line]
            comment_started = True
        elif comment_started and line_is_comment:
            # continuation of comment
            comment.append(line_is_comment.group(1))
        elif comment_started and not line_is_comment:
            # end of comment
            result.append(comment)
            comment_started = False            
        elif not comment_started and not line_is_comment:
            # continuation of non-comment
            pass
        else:
            # This should never happen
            raise RuntimeError

    return result

def short_comments(aid):
    "Scrape partial-line comments out of latex file"
    lines = readlines(fetch.latex_file_path(aid))
    return short_comments_from_lines(lines)

def short_comments_from_lines(lines):
    "Get short comments out of latex file"

    result = []
    for line in lines:
        if not re.search(long_comment_regexp, line):
            match = re.search(short_comment_regexp, line)
            if match:
                result.append(match.group(1))
    return result

def write_output(aids, long_fn, short_fn, pickle_fn=None):
    "Scrape long and short comments, write to output files."
    # If pickle_fn is given, collect everything into one dict and
    # write to a pickled python obj.  Protect this code with if's b/c
    # it can easly create a giant object that fills memory, so we
    # don't want to create this object unless it's necessary.

    if pickle_fn:
        s_result = {}
        l_result = {}

    with open(long_fn, 'w') as l_outf:
        with open(short_fn, 'w') as s_outf:
            for aid in aids:
                if verbose: print "Scraping comments from ", aid

                lines = readlines(fetch.latex_file_path(aid))

                l_comments = long_comments_from_lines(lines)
                s_comments = short_comments_from_lines(lines)

                for comment in l_comments:
                    l_outf.writelines(comment)
                    l_outf.write('\n')

                for comment in s_comments:
                    s_outf.write(comment)
                    s_outf.write('\n')

                if pickle_fn:
                    l_result[aid] = l_comments
                    s_result[aid] = s_comments

    if pickle_fn:
        util.can((l_result,s_result), pickle_fn)
