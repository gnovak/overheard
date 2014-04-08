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
def ensure_dir_exists(the_dir):
    """Make sure that the_dir exists and is a directory."""
    # This only creates the last component of the path.  If more than
    # one component is missing, there will be an error.
    if not os.path.exists(the_dir):
        os.mkdir(the_dir)
    elif not os.path.isdir(the_dir):
        raise RuntimeError, the_dir + "is not a directory!"
    
def arxiv_to_url(aid):
    "Change an archiv identifier to a URL"
    return "http://arxiv.org/e-print/" + aid

def fetch_command(aid):    
    "Give the command to fetch latex source file"
    # Direct this to file I want to avoid fussing around with incoming_tar_file_name()
    return ["wget",  "-U 'overheard'", 
            "--output-document", tar_file_name_base(aid), 
            arxiv_to_url(aid)]

def decompress_command(fn):
    "Give the command to decompress a latex source file."    
    return ["tar",  "xf", fn]

def gunzip_command(fn):
    "Give the command to decompress a latex source file."    
    # This takes place in a temporary directory: don't pass the full path, only the filename
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
    if arxiv_id.new(aid): 
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

def tar_file_name(aid, with_extension=True):
    "Filename of tar file for archive paper"
    # Get the name of the tar file.  This is complicated by the fact
    # that it may have different extensions based on file type.
    
    valid_extensions = ['.gz', '.tar', '.pdf']

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

def is_uncompressed_tar_file(fn):
    return re.search('tar archive', file_type_string(fn))

def is_gzip_file(fn):
    return re.search('gzip compressed data', file_type_string(fn))

def is_pdf_file(fn):
    return re.search('PDF document', file_type_string(fn))

def is_tex_file(fn):
    # Accept anything with the word 'text' in it.
    return re.search('text', file_type_string(fn))

def is_other_file(aid):
    # File types that are known, but that we can't do anything with
    # This is so if a file type is totally unknown, we can print a
    # message and catch it.
    return False

#def is_valid_latex(aid):
#    return (is_uncompressed_tar_file(aid) or
#            is_gzipped_tar_file(aid) or
#            is_gzipped_tex_file(aid))

#def is_valid_non_latex(aid):
#    return is_pdf(aid)

#def is_unknown(aid):    
#    return not (is_valid_latex(aid) or is_valid_non_latex(aid))

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
            ensure_dir_exists(dir)
            os.chdir(dir)
            subprocess.call(fetch_command(aid))

            # rename file to have correct extension
            if is_pdf(aid):
                shutil.move(tar_base, tar_base + '.pdf')
            elif is_gzipped_tar_file(aid) or is_gzipped_tex_file(aid):
                shutil.move(tar_base, tar_base + '.gz')                
            elif is_uncompressed_tar_file(aid):
                shutil.move(tar_base, tar_base + '.tar')
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

def get_latex(aid):
    "Get latex out of tar file"
    # Should clean up directory!
    # make things simpler by copying tar file to temp dir
    tmpdir = tempfile.mkdtemp()
    shutil.copy(tar_file_name(aid), os.path.join(tmpdir))

    with util.remember_cwd():
        os.chdir(tmpdir)
        if (is_uncompressed_tar_file(aid) or 
            is_gzipped_tar_file(aid)):
            # maybe only do this if the latex file doesn't exist?
            if verbose: print "Decompressing", aid
            subprocess.call(decompress_command(aid))
        elif is_gzipped_tex_file(aid):
            if verbose: print "gunzipping", aid
            gunzip(aid)
        elif is_unknown(aid):
            if verbose: print "Unknown file type", aid

        files = os.listdir('.')
        latex_files = [fn for fn in files
                       if extension(fn) == 'tex']
        
        # If there are no latex files, an empty file should be
        # generated to avoid later file not found errors.        
        latex_fn = latex_file_name(aid)
        dir, fn = os.path.split(latex_fn)
        ensure_dir_exists(dir)
        with open(latex_fn, 'w') as outf:
            if latex_files:
                # Can have multiple tex files, just concat them
                subprocess.call(['cat'] + latex_files, stdout=outf)
            elif is_pdf(aid):
                # Don't expect to find latex for pdf-only submissions.  
                pass
            else:
                print "Warning, no latex found for ", aid

