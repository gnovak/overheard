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
    os.makedirs(dir)
    
def arxiv_to_url(aid):
    "Change an archiv identifier to a URL"
    return "http://arxiv.org/e-print/" + aid

def fetch_command(aid):    
    "Give the command to fetch latex source file"
    # Direct this to file I want to avoid fussing around with incoming_tar_file_name()
    return (["wget",  "-U 'overheard'", 
             "--output-document", tar_file_name_base(aid)] + 
            ([] if verbose else ["--output-file", "/dev/null"]) + 
            [arxiv_to_url(aid)])
            
def decompress_command(fn):
    "Give the command to decompress a latex source file."    
    return ["tar",  "xf", fn]

def gunzip_command(fn):
    "Give the command to decompress a latex source file."    
    # This takes place in a temporary directory: don't pass the full
    # path, only the filename
    # 
    #path_name = tar_file_name(aid)
    #path, fn = os.path.split(path_name)
    return ["gunzip",  fn]

#def gunzip(aid):
#    #old_fn = aid
#    #new_fn = aid + '.gz'
#    #shutil.move(old_fn, new_fn)
#    subprocess.call(gunzip_command(aid))

def file_name_base(aid):
    "Filename of latex/tar file for archive paper without the extension"
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
    return os.path.join(path.latex, dir_prefix(aid), file_name_base(aid) + '.tex')

def tar_file_name_base(aid):
    return os.path.join(path.tar, dir_prefix(aid), file_name_base(aid))

def tar_file_name(aid):
    "Filename of tar file for archive paper"
    # Get the name of the tar file.  This is complicated by the fact
    # that it may have different extensions based on file type.
    
    valid_extensions = ['.gz', '.pdf']

    paths = [tar_file_name_base(aid) + ext 
             for ext in valid_extensions]
    exist = [os.path.isfile(pp) for pp in paths]
    n_exist = exist.count(True)

    if n_exist > 1:
        raise RuntimeError, "More than one file exists for" % aid
    elif n_exist == 0:
        # This is also used to check if the tar file exists, so if it
        # doesn't just return False without an exception.
        #
        # raise RuntimeError, "No files exist for %s" % aid 
        return False
    return paths[exist.index(True)]

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
    "Get tar file from archive.org unless we already have it"

    if tar_file_name(aid):
        if verbose: print "Using cached copy of tar file"
        return False
    else:
        with util.remember_cwd():            
            tar_base = tar_file_name_base(aid)
            dir, fn = os.path.split(tar_base)
            ensure_dirs_exist(tar_base)
            os.chdir(dir)
            subprocess.call(fetch_command(aid))

            # rename file to have correct extension
            if is_pdf(tar_file_name_base(aid)):
                shutil.move(tar_base, tar_base + '.pdf')
            elif is_gzip(tar_file_name_base(aid)):
                shutil.move(tar_base, tar_base + '.gz')                
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
    "Get latex out of tar file"
    # Should clean up directory!
    path_name = tar_file_name(aid)
    if not path_name:
        # could just try to grab the file from arxiv.org here.  
        raise ValueError, "File not found for %s!" % aid 
    tmpdir = tempfile.mkdtemp()    
    shutil.copy(path_name, os.path.join(tmpdir))
    with util.remember_cwd():
        # All of this is taking place in a temp dir
        # Strip off path names
        base_path_name = tar_file_name_base(aid)    
        junk, base_fn = os.path.split(base_path_name)
        junk, ext_fn = os.path.split(path_name)

        os.chdir(tmpdir)
        # gunzip if necessary
        if is_gzip(ext_fn):
            if verbose: print "Decompressing", aid            
            subprocess.call(gunzip_command(ext_fn))
        
        if is_tex(base_fn):
            # if it's a tex file, rename to correct extension
            shutil.move(base_fn, base_fn + '.tex')
        elif is_tar(base_fn):
            # if it's a tar file, extract
            subprocess.call(decompress_command(base_fn))
        elif is_pdf(ext_fn):
            # pdf files still have extension
            pass
        elif is_other(base_fn):
            # Everything except pdf files has been decompressed
            pass
        else:
            print "Unknown file type %s !" % aid

        # All Latex files should now have .tex extensions, collect them.
        files = os.listdir('.')
        latex_files = [fn for fn in files if extension(fn) == 'tex']
        
        # If there are no latex files, an empty file should be
        # generated to avoid later file not found errors.        
        latex_fn = latex_file_name(aid)
        ensure_dirs_exist(latex_fn)
        with open(latex_fn, 'w') as outf:
            if latex_files:
                # Can have multiple tex files, just concat them
                subprocess.call(['cat'] + latex_files, stdout=outf)

