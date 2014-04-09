#!/opt/local/bin/python
################
# Ideas, Todos #
################
# 
# Small Improvements
# - Start downloading all papers, not just astro-ph
# - Some people put dirs in their tar files, could use walk_tree
#   instead of listdir
# - Actually second run took 8.5 min, so... acceptable overheard.
# - Some people don't put linebreaks -- short comments > 80 chars are
#   really long comments.  Should maybe clean linebreaks, %'s out of
#   long comments anyway.
# - Move paths to latex and data dirs to config file
# - Detect if I'm getting stonewalled by arxiv.org
# - Allow partial line /full line to be "long comment"?
# - Package up into "official" python package
# - Keep record of which comments came from which papers?
# - Handle both .gz and .pdf papers existing -- 1401.0908 was PDF-only
#   (so there was a PDF in the source dir) but then withdrawn, which
#   generated a .gz file containing the text file 'withdrawn.'  This
#   caused the code to barf, but I _think_ that's the only case that
#   can lead to this.  So just handle it, maybe w/ a warning.
# - Check for files with pdf extension 
#
# Large improvements
# - Handle multiple versions of each paper
#   + Fetch all versions of papers
#   + Turn off caching when downloading new papers so we get replacements
#   + Explicitly put in version ids to avoid overwriting
# - Handle character encoding
# - More efficient tweet finding
#   + Would like blacklist and whitelist -- kill 'boilerplate' comments,
#     definitely keep anything with 'fuck' in it.
#   + Some kind of filtering... blacklist/whitelist.  Always keep
#     comments infolving profanity, but always take out boilerplate from
#     sample files.
#   + Automated filtering?
#   + Collaborative filtering?
#   + Want some kind of clustering: unusual comments: use words that
#     typically don't appear in sci papers.  Could look for non-comment
#     lines and then look for comment lines.
#
# Other todos
# - Post to github
#
# Other ideas
# - Make web site that allows you to feed archive ids and get comments?
# - Take papers from ADS search, arxiv search?
#
#########
# Notes #
#########
# 
# - Shell command dependencies:
#   wget, tar, file, cat, gzip
#

import sys, os, datetime, argparse

import path, update, fetch, scrape

def process_todays_papers(delay=60, prefix='.', nmax=None):
    "Download today's papers and extract comments"
    # nmax is for testing to specify that a small number of papers
    # should be fetched.

    date_str = datetime.date.today().isoformat()
    long_fn = os.path.join(prefix, date_str + '-long.tex')
    short_fn = os.path.join(prefix, date_str + '-short.tex')

    aids = update.parse_rss()
    if not nmax is None: aids = aids[:min(len(aids), nmax)]
    fetch.all_source(aids, delay=delay)
    fetch.all_latex(aids)    
    scrape.write_output(aids, long_fn, short_fn)

def main(argv=None):
    if argv is None: argv = sys.argv

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress progress messages', )
    parser.add_argument('-d', '--delay', type=int, default=10, 
                        help="Delay in sec between requests to arxiv.org", )
    parser.add_argument('-u', '--user-agent', 
                        help="User agent string to use for requests to arxiv.org")

    args = parser.parse_args(argv[1:])
    fetch.user_agent = args.user_agent
    fetch.verbose = update.verbose = not args.quiet

    process_todays_papers(delay=args.delay)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    sys.exit(main())
