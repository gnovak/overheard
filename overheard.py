# Ideas:
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

import re, tempfile, os, contextlib, subprocess, shutil, cPickle, time, datetime

import feedparser

# Shell command dependencies:
# wget, tar, file, cat, gzip

# Make these into absolute paths to make it easy to find files
exec_dir = os.getcwd()
tar_dir = os.path.join(exec_dir, 'data')
latex_dir = os.path.join(exec_dir, 'latex')

# Separate short comments (less than full line) from long comments (at
# least one full line) because long comments are sometimes full paragraphs.

# Backslash-percent (to get percent into the latex output) shows up in
# the python strings as "\\%" and a regexp for just '%' doesn't match
# them, which simplifies my life...

# long comment is 'optional whitepace % comment'
long_comment_regexp = "^\s*(%.*)$"

# Short comment is "string including at least one non-whitespace char
# and not including percent, percent, any string."  Can't find a
# regexp that matches 'some % comment % and more' but not ' % comment
# $ and more' which is a long comment.  Therefore define a short
# comment to be "some string + longest string starting with percent,
# that doesn't also match long_comment_regexp"
short_comment_regexp = '.*?(%.*)$'

### Code snippet from http://stackoverflow.com/questions/169070/
@contextlib.contextmanager
def remember_cwd():
    curdir= os.getcwd()
    try: yield
    finally: os.chdir(curdir)
### End snippet from Stackexchange

### Code snippet from gsn_util package
### https://pypi.python.org/pypi/gsn_util/
def can(obj, file, protocol=2):
    """More convenient syntax for pickle, intended for interactive use

    Most likely:
    >>> can([1,2,3], 'file.dat')
    But can also do:
    >>> with open('file.dat', 'w') as f: can([1,2,3], f); can((3,4,5), f)

    """
    if type(file) is str: f=open(file,'wb')
    else: f=file

    cPickle.dump(obj, f, protocol=protocol)

    if type(file) is str: f.close()

def uncan(file):
    """More convenient syntax for pickle, intended for interactive use

    Most likely:
    >>> obj = uncan('file.dat')
    But can also do:
    >>> with open('file.dat') as f: foo = uncan(f); bar = uncan(f)

    """
    # If filename, should this read until all exhausted?
    if type(file) is str: f=open(file, 'rb')
    else: f=file    

    obj = cPickle.load(f)

    if type(file) is str: f.close()

    return obj
### End code snippet from gsn_util package

def extension(fn):
    "Get the extension of a filename"
    return os.path.splitext(fn)[1][1:]

def old_arxiv_id(aid):
    "Is this an old-style arxiv id?"
    # old-style identifier is seven digits, yymmNNN
    return re.search('^[0-9]{7}(v[0-9]+)?$', aid)

def new_arxiv_id(aid):
    "Is this an new-style arxiv id?"
    # new-style identifier is is 4 digits, dot, 4 digits:
    # yymm.NNNN
    return re.search('^[0-9]{4}.[0-9]{4}(v[0-9]+)?$', aid)

def arxiv_to_url(aid):
    "Change an archiv identifier to a URL"
    if new_arxiv_id(aid):
        return "http://arxiv.org/e-print/" + aid
    elif old_arxiv_id(aid):
        return "http://arxiv.org/e-print/astro-ph/" + aid
    else:
        raise ValueError
 
def fetch_command(aid):
    "Give the command to fetch latex source file"
    return ["wget",  "-U 'overheard'", arxiv_to_url(aid)]

def decompress_command(aid):
    "Give the command to decompress a latex source file."    
    return ["tar",  "xf", tar_file_name(aid)]

def gunzip_command(aid):
    "Give the command to decompress a latex source file."    

def gunzip(aid):
    old_fn = aid
    new_fn = aid + '.tex.gz'
    shutil.copy(old_fn, new_fn)
    subprocess.call(["gunzip",  new_fn])

def latex_file_name(aid):
    "Filename of latex source file for archive paper"
    return os.path.join(latex_dir, aid + '.tex')

def tar_file_name(aid):
    "Filename of tar file for archive paper"
    return os.path.join(tar_dir, aid)

def file_type_string(aid):
    "Must filter out PDF only papers"
    # Find out what kind of file it is.
    pipe = subprocess.Popen(["file", tar_file_name(aid)], stdout=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    return stdout

def is_uncompressed_tar_file(aid):
    return re.search('tar', file_type_string(aid))

def is_gzipped_tar_file(aid):
    return re.search('gzip compressed data, from', file_type_string(aid))

def is_gzipped_tex_file(aid):
    return re.search('gzip compressed data, was', file_type_string(aid))

def is_pdf(aid):
    return re.search('PDF', file_type_string(aid))

def is_valid_latex(aid):
    return (is_uncompressed_tar_file(aid) or
            is_gzipped_tar_file(aid) or
            is_gzipped_tex_file(aid))

def is_valid_non_latex(aid):
    return is_pdf(aid)

def is_unknown(aid):    
    return not (is_valid_latex(aid) or is_valid_non_latex(aid))

def fetch_all_latex(aids, delay=60):
    for aid in aids:
        wait = fetch_latex(aid)
        if wait:
            time.sleep(delay)

def fetch_latex(aid):
    "Get tar file from archive.org unless we already have it"
    
    if os.path.exists(tar_file_name(aid)):
        print "Using cached copy of tar file"
        return False
    else:
        with remember_cwd():
            os.chdir(tar_dir)
            subprocess.call(fetch_command(aid))
        return True

def get_all_latex(aids):
    for aid in aids:
        get_latex(aid)

def get_latex(aid):
    "Get latex out of tar file"
    # Should clean up directory!
    # make things simpler by copying tar file to temp dir
    tmpdir = tempfile.mkdtemp()
    shutil.copyfile(tar_file_name(aid), 
                    os.path.join(tmpdir, aid))
    home_dir = os.getcwd()
    with remember_cwd():
        os.chdir(tmpdir)
        if (is_uncompressed_tar_file(aid) or 
            is_gzipped_tar_file(aid)):
            # maybe only do this if the latex file doesn't exist?
            print "Decompressing", aid
            subprocess.call(decompress_command(aid))
        elif is_gzipped_tex_file(aid):
            print "gunzipping", aid
            gunzip(aid)
        elif is_unknown(aid):
            print "Unknown file type", aid

        files = os.listdir('.')
        latex_files = [fn for fn in files
                       if extension(fn) == 'tex']
        
        # If there are no latex files, an empty file should be
        # generated to avoid later file not found errors.
        with open(latex_file_name(aid), 'w') as outf:
            if latex_files:
                # Can have multiple tex files, just concat them
                subprocess.call(['cat'] + latex_files, stdout=outf)
            else:
                print "Warning, no latex found for ", aid

def scrape_long_comments(aid):
    "Get long comments out of latex file"

    with open(latex_file_name(aid)) as ff:
        lines = ff.readlines()

    # State variable
    comment_started = False
    # Contains current comment
    comment = []
    # Contains list of all comments -- overall output
    result = []

    for line in lines:
        # Full-line comment is anything that has only whitespace and a
        # comment character at the beginning
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

def scrape_short_comments(aid):
    "Get short comments out of latex file"
    with open(latex_file_name(aid)) as ff:
        lines = ff.readlines()

    result = []
    for line in lines:
        if not re.search(long_comment_regexp, line):
            match = re.search(short_comment_regexp, line)
            if match:
                result.append(match.group(1))
    return result

def fetch_rss_maybe():
    """Get RSS feed.  Cache it to avoid hitting their server continuously
    while testing"""
    if False and os.path.exists('rss-feed.dat'):
        print "Using cached copy of rss feed"
        return uncan('rss-feed.dat')
    else:
        feed = feedparser.parse('http://arxiv.org/rss/astro-ph')
        can(feed, 'rss-feed.dat')
        return feed

def parse_rss_feed():
    feed = fetch_rss_maybe()
        
    result = [ re.search('.*/([0-9.v]*$)', entry['id']).group(1)
               for entry in feed['entries']]
    return result

def write_output(aids, long_outfn, short_outfn):

    with open(long_outfn, 'w') as outf:
        for aid in aids:
            comments = scrape_long_comments(aid)
            for comment in comments:
                outf.writelines(comment)
                outf.write('\n')

    with open(short_outfn, 'w') as outf:
        for aid in aids:
            comments = scrape_short_comments(aid)
            for comment in comments:
                outf.write(comment)
                outf.write('\n')
    

def scrape_all_comments(aid):
    "Get comments out of latex file"
    with open(latex_file_name(aid)) as ff:
        lines = ff.readlines()
    short_comments = scrape_short_comments(lines)
    long_comments = scrape_long_comments(lines)        
    return short_comments, long_comments


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
    for the_dir in [tar_dir, latex_dir]:        
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
