import os, cPickle, contextlib

### Code snippet from http://stackoverflow.com/questions/169070/
@contextlib.contextmanager
def remember_cwd():
    """Restore the present current working directory when finished."""
    curdir= os.getcwd()
    try: yield
    finally: os.chdir(curdir)
### End snippet from Stackexchange

### Code snippet from gsn_util package
### https://pypi.python.org/pypi/gsn_util/

def flatten(L):
    """Return a flat list with the same elements as arbitrarily nested
    list L"""
    def rec(lst):
        for el in lst:
            if type(el) is not type([]):
                result.append(el)
            else:
                rec(el)
    result = []
    rec(L)
    return result
#
# These were used for caching the rss feed, but they're not currently used anywhere.
# 
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
