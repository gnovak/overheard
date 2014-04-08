#########
# Notes #
#########
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
# All of these are listed as 'data' after gunzipping, even though it
# looks like fine latex to me.
# 
# 1303.5083 1401.5069 1401.5758 1401.5838 1401.6077 1401.6577
# 1401.7056 1402.0695 1402.0700 1402.1495 1402.1968 1402.5880
# 1403.2389 1403.3804
# 
# archive.org Won't accept wget user agent string, can be anything else
# 
# Fetching source files (same for old and new archive identifiers)
#  0408420 gives most recent
#  0408420vN gives version N
#  0408420vN if N > number of versions gives most recent version
#

import os, subprocess, tempfile, shutil, re, time

import path, util, arxiv_id

verbose = True

# arxiv_id's job is parsing arxiv identifiers.  This module's job is
# relating that to the filesystem.  The entire archive is partitioned
# into directories that are just the yymm part of the arxiv id, so
# just steal that function from the arxiv_id module.
dir_prefix = arxiv_id.yymm

def extension(fn):
    "Get the extension of a filename"
    return os.path.splitext(fn)[1][1:]

# Maybe make this take a full path with filename and create all
# leading dirs to avoid having to split it apart
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
    "Change an archiv identifier to a URL"
    return "http://arxiv.org/e-print/" + aid

def fetch_command(aid):    
    "Give the command to fetch latex source file"
    # Direct this to file I want to avoid fussing around with incoming_tar_file_name()
    return (["wget",  "-U 'overheard'", 
             "--output-document", source_file_path_without_extension(aid)] + 
            ([] if verbose else ["--output-file", "/dev/null"]) + 
            [arxiv_to_url(aid)])
            
def untar_command(fn):
    "Give the command extract a tar archive."    
    return ["tar",  "xf", fn]

def gunzip_command(fn):
    "Give the command to decompress a gzip file."    
    return ["gunzip",  fn]

#def gunzip(aid):
#    #old_fn = aid
#    #new_fn = aid + '.gz'
#    #shutil.move(old_fn, new_fn)
#    subprocess.call(gunzip_command(aid))

def file_name_base(aid):
    "Filename of latex/source file for an arxiv id without the extension"
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
    "Filename of latex source file for archive paper"
    return file_name_base(aid) + '.tex'

def latex_file_path(aid):
    "Filename of latex source file for archive paper"
    return os.path.join(path.latex, dir_prefix(aid), latex_file_name(aid))

def source_file_name(aid):
    "Filename of source file for archive paper"
    ext = source_file_extension(aid)
    if not ext:
        raise RuntimeError, "No files exist for %s" % aid 
    return file_name_base(aid) + ext

def source_file_path(aid):
    "Filename of source file for archive paper"
    return os.path.join(path.source, dir_prefix(aid), source_file_name(aid))

def source_file_path_without_extension(aid):
    # This is used just after downloading a file, when it doesn't have
    # the correct extension yet b/c we don't know the file type.
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
        raise RuntimeError, "More than one file exists for" % aid
    elif n_exist == 0:
        return False
        
    return valid_extensions[exist.index(True)]

def file_type_string(fn):
    "Find out what kind of file it is."

    pipe = subprocess.Popen(["file", fn], stdout=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    return stdout

def is_tar(fn):
    return re.search('tar archive', file_type_string(fn))

def is_gzip(fn):
    return re.search('gzip compressed data', file_type_string(fn))

def is_pdf(fn):
    return re.search('PDF document', file_type_string(fn))

def is_tex(fn):
    # Accept anything with the word 'text' in it.
    return re.search('text', file_type_string(fn))

def is_other(aid):
    # File types that are known, but that we can't do anything with
    # This is so if a file type is totally unknown, we can print a
    # message and catch it.
    return False

def fetch_all_latex(aids, delay=60):
    for aid in aids:
        wait = fetch_latex(aid)
        if wait:
            time.sleep(delay)

def fetch_latex(aid):
    "Get source file from archive.org unless we already have it"

    if source_file_exists(aid):
        if verbose: print "Using cached copy of source file"
        return False
    else:
        source_base = source_file_path_without_extension(aid)
        ensure_dirs_exist(source_base)
        subprocess.call(fetch_command(aid))

        # rename file to have correct extension
        if is_pdf(source_base):
            shutil.move(source_base, source_base + '.pdf')
        elif is_gzip(source_base):
            shutil.move(source_base, source_base + '.gz')                
        # bare tar files don't appear in "official" archive, don't
        # create them here.
        #elif is_uncompressed_tar_file(tar_file_name_base(aid)):
        #    shutil.move(tar_base, tar_base + '.tar')
        else:
            # This should/would be an exception, but it occurs
            # when downloading the new astro-ph files for the day.
            # I don't want an unrecognized file to prevent
            # downloading other papers, so just print a message
            # and move on.
            # 
            # raise RuntimeError, "Unrecognized file %s" % aid
            print "WARNING: Unrecognized file type for %s!" % aid
        return True

def get_all_latex(aids):
    for aid in aids:
        get_latex(aid)


# Looking at two months worth of actual submissions, what do I learn?
# - There are two extensions allowed: pdf and gz
# - The output of 'file' on the gzip files is sometimes bizarrely
#   incorrect.  See below, which contain valid latex files:
#  
#   1211.0074.gz:  Minix filesystem, V2, 51878 zones
#   cond-mat0701210.gz:  gzip compressed data, was "/data/new/0022/0022418/src/with", 
#   math0701257.gz:      x86 boot sector, code offset 0x8b
# 
# - It's fine to gunzip stuff, it doesn't decompress to the original
#   filename, but rather from 1234.1234.gz to 1234.1234
# - After gunzipping, several things can be there:
#   + latex file
#   + tar file
#   + postscript
#   + pdf (maybe not?)
#   + html
#   + text file
# - So the procedure is:
#   + gunzip file
#   + If it's a latex file, rename to *.tex
#   + If it's a tar file, untar
#   + Could conceivably scrape html for comments but that doesn't seem
#     like it will be very fruitful
#   + Any other file type, I don't really care about.
#
#
# Reliably finding out if something is latex isn't so easy.  All kinds
# of crazy stuff with comes up with "text" in it.  Sometimes you get
# 'data' or 'Latex auxilliary file'  Examples below:
# 
# 1303.5083.tex: data
# 1401.5069.tex: data
# 1401.5758.tex: data
# 1401.5838.tex: data
# 1401.6077.tex: data
# 1401.6577.tex: data
# 1401.7056.tex: data
# 1402.0695.tex: data
# 1402.0700.tex: data
# 1402.1495.tex: data
# 1402.1968.tex: data
# 1402.5880.tex: data
# 1402.7083.tex: LaTeX auxiliary file
# 1403.1644.tex: data
# 1403.2389.tex: data
# 1403.3804.tex: data

def get_latex(aid):
    "Get latex out of source file"
    # Should clean up directory!
    if not source_file_exists(aid):
        # could just try to grab the file from arxiv.org here.  
        raise ValueError, "File not found for %s!" % aid 
    path_name = source_file_path(aid)
    tmpdir = tempfile.mkdtemp()    
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
            print "Unknown file type %s !" % aid

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

