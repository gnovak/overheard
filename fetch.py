#########
# Notes #
#########
# 
# Archive.org won't accept wget user agent string---it can be anything else
# 
# When fetching source files from arxiv.org: 
#  0408420 gives most recent
#  0408420vN gives version N
#  0408420vN if N > number of versions gives most recent version
# (the behavior is same for old and new archive identifiers)
#
# The conventions for storing latex source archives files are taken
# from those used in the bulk data made available by arxiv.org via
# Amazon.com's S3 service.  This makes it possible to download a bunch
# of source files, untar them, and start working on the data without
# pre-processing the files in any way.
# 
# Information here: http://arxiv.org/help/bulk_data_s3
# 
# Command to bulk download arxiv sources to the current directory
# s3cmd sync --add-header="x-amz-request-payer: requester" s3://arxiv/src/ .
#
# The entire archive is divided into sub-directories by YYMM.  Files
# in each directory can be pdf files or gzip files.  The gunzipped
# file can be any number of things: latex source, a tar file,
# postscript, html, plain text, (and more?).  It might have been nice
# if the pdf files were gzipped so that _everything_ could be handled
# the same way (gunzip, figure out what it is, act appropriately), but
# the arxiv.org people have decided not to do that.  It's true that
# PDF files are already compressed, so gzipping them is kind of a
# waste.
# 
# However, when you download a paper via
# http://arxiv.org/e-print/identifier, you don't know if the file will
# be a PDF or a gzip file, and the resulting file has no extension.
# Therefore when fetching papers (from the arxiv.org RSS feed, for
# instance), the code below looks at the file type and puts the
# appropriate extension so that it goes into the data directory just
# like the bulk data provided by arxiv.org via S3.  
#
# Thus when you ask for the name of the data file associated with an
# arxiv id, you may want it without an extension (if it was downloaded
# via wget and you want to put the appropriate extension on), or you
# may want it _with_ the extension (in which case the code must look
# to see if it's a pdf or gz file, and give you the correct filename).
# 
# Note that it's necessary to call 'file' on the gunzipped file.
# Calling 'file' on the gzipped file allows you to figure out what's
# inside most of the time, but sometimes the results are hilariously
# wrong.  All of these contain valid latex:
#   1211.0074.gz:  Minix filesystem, V2, 51878 zones
#   cond-mat0701210.gz:  gzip compressed data, was "/data/new/0022/0022418/src/with", 
#   math0701257.gz:      x86 boot sector, code offset 0x8b
#
# Even calling file on the gunzipped file is bizarrly incorrect
# sometimes -- files are listed as C++, plain text (when they're
# latex), or even 'data'.  As long as the output of 'file' has the
# word 'text' in it, I treat it as latex.  
# 
# The problem with files not being recognized as latex after
# gunzipping apparently has to do with text encodings.  Here are a few
# examples of arxiv id's listed as 'data' after gunzipping.
# 1303.5083 1401.5069 1401.5758 1401.5838 1401.6077 1401.6577
# 1401.7056 1402.0695 1402.0700 1402.1495 1402.1968 1402.5880
# 
# All of the above is for file v5.04 on OS X 10.9.2 Mavaricks.  This
# version of file dates from about 2010 and I'm writing this in 2014.
# Going to the latest version of file v5.17 results in improvements in
# the file type determination for about 300 of the ~3000 files in the
# entire archive of 1 million papers, so, it's not really worth it.
#
# In any case, using file v5.17 installed from MacPorts results in
# messages like:
# ERROR: line 163: regex error 17, (illegal byte sequence)
# This is evidently another text encoding problem and it is discussed here:
# https://trac.macports.org/ticket/38771
# A workaround is to set the shell variables:
# export LC_CTYPE=C 
# export LANG=C
# 
# There's other weird stuff in the files provided by arxiv.org, like
# PDF files that 'file' reports to be strange things.  All of these
# are viewable via Emacs DocView and Apple Preview, although when you
# look at the bytes they do indeed look weird (not like normal PDF
# files).
# ./0003/cond-mat0003162.pdf: data
# ./0304/cond-mat0304406.pdf: MacBinary III data with surprising version number
# ./0404/physics0404071.pdf: data
# ./9803/cond-mat9803359.pdf: data
# ./9805/cond-mat9805146.pdf: data
# ./0402/cs0402023.pdf: POSIX tar archive (GNU)
# ./1204/1204.0257.pdf: data
# ./1204/1204.0258.pdf: data
# 
# It takes ~5.5 min to just gunzip everything and untar everything via
# the shell for one month's sumbissions.  takes ~10 min to do it via
# python code.  I find this acceptable.
# 

import sys, os, subprocess, tempfile, shutil, re, time

import path, util, arxiv_id

# Interactive use/testing more or less requires that fetch.user_agent
# be set to something here in the source file.  However, I don't want
# other people hammering arxiv.org with a user agent string that looks
# like it's me.  Therefore the arg parsing code in overheard.py sets
# fetch.user_agent to None if the value isn't provided on the command
# line.  That triggers an error message if wget is called.

user_agent = 'overheard'

verbose = True

# arxiv_id's job is parsing arxiv identifiers.  This module's job is
# relating that to the filesystem.  The entire archive is partitioned
# into directories that are just the yymm part of the arxiv id, so
# just steal that function from the arxiv_id module.

dir_prefix = arxiv_id.yymm

def extension(fn):
    "Get the extension of a filename"
    return os.path.splitext(fn)[1][1:]

def ensure_dirs_exist(path_name):
    """Ensure that dirs exist to create a file
    
    path_name is expected to be the path to a file, including the
    filename.  This creates all of the directories leading up to the
    filename.  

    If path_name ends with a path separator, then the last element is
    known to be a directory and the entire path is created if it
    doesn't exist.

    """    
    dir, fn = os.path.split(path_name)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    
def arxiv_to_url(aid):
    "Get the URL to download the source file for a paper"
    return "http://arxiv.org/e-print/" + aid

def fetch_command(aid, fn):    
    "Give the command to fetch latex source file"
    # Explicitly give the output file name because old-style arxiv
    # id's result in files like 9901012 that lack the archive name.

    if user_agent is None:        
        print >> sys.stderr, "User agent string not set.  Arxiv.org blocks requests with the user"
        print >> sys.stderr, "agent string wget.  You must set a different one like this:"
        print >> sys.stderr
        print >> sys.stderr, "%s -u 'my user agent string'" % sys.argv[0]
        print >> sys.stderr
        sys.exit(1)

    return (["wget",  "-U '%s'" % user_agent, 
             "--output-document", fn] + 
            ([] if verbose else ["--output-file", "/dev/null"]) + 
            [arxiv_to_url(aid)])
            
def untar_command(fn):
    "Give the command extract a tar archive."    
    return ["tar",  "xf", fn]

def gunzip_command(fn):
    "Give the command to decompress a gzip file."    
    return ["gunzip",  fn]

def file_name_base(aid):
    "Name of latex/source file for an arxiv id without the extension"
    if arxiv_id.is_new(aid): 
        fn_base = aid
    else: 
        # Ugh, four function calls when I could just grab the regexp
        # match object and pull out what I want.  And all of this is
        # just to get rid of the slash in the identifier
        fn_base = (arxiv_id.archive(aid) + arxiv_id.yymm(aid) + 
                   arxiv_id.number(aid) + arxiv_id.version(aid))
    return fn_base

def latex_file_name(aid):
    "Name of latex file"
    return file_name_base(aid) + '.tex'

def latex_file_path(aid):
    "Full path to the latex file"
    return os.path.join(path.latex, dir_prefix(aid), latex_file_name(aid))

def source_file_name(aid):
    "Name of source file"
    ext = source_file_extension(aid)
    if not ext:
        raise RuntimeError, "No files exist for %s" % aid 
    return file_name_base(aid) + ext

def source_file_path(aid):
    "Full path to source file"
    return os.path.join(path.source, dir_prefix(aid), source_file_name(aid))

def source_file_path_without_extension(aid):
    """Full path to source file without the extension

    This is used when figuring out the correct extension of the source
    file for this particular paper

    """
    return os.path.join(path.source, dir_prefix(aid), file_name_base(aid))

def source_file_exists(aid):
    """Determine if the source file associated with an arxiv id exists."""
    return source_file_extension(aid) 

def source_file_extension(aid):
    """Return the extension of the source file associated with an arxiv id.

    Return False if the file doesn't exist.

    """
    valid_extensions = ['.gz', '.pdf']

    paths = [source_file_path_without_extension(aid) + ext 
             for ext in valid_extensions]
    exist = [os.path.isfile(pp) for pp in paths]
    n_exist = exist.count(True)

    if n_exist > 1:
        raise RuntimeError, "More than one file exists for %s" % aid
    elif n_exist == 0:
        return False
        
    return valid_extensions[exist.index(True)]

def file_type_string(fn):
    "Return the output of the 'file' command"

    pipe = subprocess.Popen(["file", fn], stdout=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    return stdout

def is_tar(fn):
    "Is this a tar file?"
    return re.search('tar archive', file_type_string(fn))

def is_gzip(fn):
    "Is this a gzip file?"
    return re.search('gzip compressed data', file_type_string(fn))

def is_pdf(fn):
    "Is this a pdf file?"
    return re.search('PDF document', file_type_string(fn))

def is_tex(fn):
    "Is this a latex file?"
    # Accept anything with the word 'text' in it.
    return re.search('text', file_type_string(fn))

def is_other(fn):
    "Is this some file that we recognize but don't do anything with?"
    # File types that are known, but that we can't do anything with
    # This is so if a file type is totally unknown, we can print a
    # message and catch it.
    return re.search('TeX DVI', file_type_string(fn))

def all_source(aids, delay=60, force=False):
    """Fetch the source files for all of the given arxiv ids.
    
    delay is delay in seconds between fetching papers from arxiv.org
    force=True disables caching of papers
    """
    any_fetched = False
    for aid in aids:
        wait = source(aid, force=force)
        if wait:
            any_fetched = True
            time.sleep(delay)
    return any_fetched

def source(aid, force=False):    
    "Get source file from archive.org unless we already have it"

    if not force and source_file_exists(aid):
        if verbose: print "Using cached source file for", aid
        return False
    else:
        # Interrupted downloads leave partial files laying around.
        # Download to temp directory, then rename to final filename to
        # avoid polluting the archive.
        tf = tempfile.NamedTemporaryFile()
        subprocess.call(fetch_command(aid, tf.name))

        source_base = source_file_path_without_extension(aid)
        ensure_dirs_exist(source_base)
        # copy file to have correct extension.  User copy rather than
        # move so the system can happily delete the temp file when
        # it's closed.
        if is_pdf(tf.name):
            shutil.copy(tf.name, source_base + '.pdf')
        elif is_gzip(tf.name):
            shutil.copy(tf.name, source_base + '.gz')
        else:
            # This should/would be an exception, but it occurs
            # when downloading the new astro-ph files for the day.
            # I don't want an unrecognized file to prevent
            # downloading other papers, so just print a message
            # and move on.
            # 
            # raise RuntimeError, "Unrecognized file %s" % aid
            print "WARNING: Unrecognized file type for", aid
        return True

def all_latex(aids):
    """Extract latex from all arxiv ids given."""
    for aid in aids:
        latex(aid)

def latex(aid):
    "Get latex out of source file"

    if not source_file_exists(aid):
        # could just try to grab the file from arxiv.org here.  
        raise ValueError, "File not found for %s!" % aid 

    path_name = source_file_path(aid)
    tmpdir = tempfile.mkdtemp()    
    try:
        shutil.copy(path_name, tmpdir)    
        with util.remember_cwd():
            # All of this is taking place in a temp dir, so I only want
            # filenames, not paths.
            os.chdir(tmpdir)

            base_fn = file_name_base(aid)
            ext_fn = source_file_name(aid)

            # gunzip if necessary
            if is_gzip(ext_fn):
                if verbose: print "Decompressing", aid            
                subprocess.call(gunzip_command(ext_fn))

            if is_tex(base_fn):
                # if it's a tex file, rename to correct extension
                shutil.move(base_fn, base_fn + '.tex')
            elif is_tar(base_fn):
                # if it's a tar file, extract
                if verbose: print "Extracting", aid            
                subprocess.call(untar_command(base_fn))
            elif is_pdf(ext_fn):
                # pdf files still have extension, so look at the filename
                # with extension.
                pass
            elif is_other(base_fn):
                # Everything except pdf files has been decompressed, so
                # look at the filename without the extension.
                pass
            else:
                # The line break comes at the end of file_type_string()
                print "WARNING: Unknown file type: ", file_type_string(base_fn), 
            # All Latex files should now have .tex extensions, collect them.
            files = os.listdir('.')
            latex_files = [fn for fn in files if extension(fn) == 'tex']

            # If there are no latex files, an empty file should be
            # generated to avoid later file not found errors.        
            latex_fn = latex_file_path(aid)
            ensure_dirs_exist(latex_fn)
            with open(latex_fn, 'w') as outf:
                if latex_files:
                    # Can have multiple tex files, just concat them
                    subprocess.call(['cat'] + latex_files, stdout=outf)
    finally:
        shutil.rmtree(tmpdir)
                    
