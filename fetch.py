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
    if arxiv_id.new(aid):
        return "http://arxiv.org/e-print/" + aid
    elif arxiv_id.old(aid):
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
    return os.path.join(path.latex, aid + '.tex')

def tar_file_name(aid):
    "Filename of tar file for archive paper"
    return os.path.join(path.tar, aid)

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
        if verbose: print "Using cached copy of tar file"
        return False
    else:
        with util.remember_cwd():
            os.chdir(path.tar)
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
        with open(latex_file_name(aid), 'w') as outf:
            if latex_files:
                # Can have multiple tex files, just concat them
                subprocess.call(['cat'] + latex_files, stdout=outf)
            else:
                print "Warning, no latex found for ", aid

