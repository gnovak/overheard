#!/opt/local/bin/python
# 
#########
# Notes #
#########
# 
# Shell command dependencies:
# wget, tar, file, cat, gzip
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
    "Download today's papers and extract comments"
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
    fetch.verbose = scrape.verbose = not args.quiet

    process_todays_papers(delay=args.delay)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    sys.exit(main())
