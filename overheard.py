# Ideas:
# - add force option to fetch.fetch_latex
# - fix fetch.fetch_latex and fetch.get_latex names
# - make predicates is_blah
# - Make web site that allows you to feed archive ids and get comments
# - Astro-ph diff: using latexdiff?  Or just diff of tex file?
# - Take papers from RSS feed
# - Take papers from ADS search
# - Take papers from arxiv search
# - Some kind of filtering... take out boilerplate, for instance
# - Look into automated interface
# - Detect if I'm getting stonewalled by arxiv.org
# - Put delays into file fetching...
# - upload to github
# - Keep record of tweets, look for comments similar to them.
# - clean code a little
# - Post to github
# - Snarf input from arxiv mailing
# - Allow partial line /full line to be "long comment"?
# - remove temp dir

# - Want some kind of clustering: unusual comments: use words that
#   typically don't appear in sci papers.  Could look for non-comment
#   lines and then look for comment lines.
# - Would like blacklist and whitelist -- kill 'boilerplate' comments,
#   definitely keep anything with 'fuck' in it.

# Notes:
#
# archive.org Won't accept wget user agent string, can be anything else
# 
# Fetching tar files (same for old and new archive identifiers)
#  0408420 gives most recent
#  0408420vN gives version N
#  0408420vN if N > number of versions gives most recent version


# Split into:
# map arxiv id to path
# extract latex
# extract comments
# util
# dealing with arxiv ids
# dealing with filenames
# Shell commands...?
# RSS feed/downloading new papers
# main


import re, tempfile, os, subprocess, shutil, time, datetime

import feedparser

import path

# Shell command dependencies:
# wget, tar, file, cat, gzip

# Separate short comments (less than full line) from long comments (at
# least one full line) because long comments are sometimes full paragraphs.

# Backslash-percent (to get percent into the latex output) shows up in
# the python strings as "\\%" and a regexp for just '%' doesn't match
# them, which simplifies my life...

def do_it_all(long_outfn, short_outfn):
    aids = parse_rss_feed()
    fetch_all_latex(aids, delay=60)
    get_all_latex(aids)    
    write_output(aids, long_outfn, short_outfn)

def download_todays_papers():
    aids = parse_rss_feed()
    fetch_all_latex(aids, delay=60)

def main():
    # Ensure required directories exist
    for the_dir in [path.tar, path.latex]:        
        if not os.path.exists(the_dir):
            os.mkdir(the_dir)
        elif not os.path.isdir(the_dir):
            raise RuntimeError, the_dir + "is not a directory!"

    date_str = datetime.date.today().isoformat()
    do_it_all(date_str + '-long.tex', date_str + '-short.tex')

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    main()
