import sys
from distutils.core import setup

args = dict(name='overheard',
            version='1.1',
            license='MIT (X11) License',
            author='Greg Novak',
            author_email='greg.novak@gmail.com',
            packages=['overheard'],
            # http://github.org/overheard
            # url='http://pypi.python.org/pypi/overheard/',
            description='Overheard on Astro-ph',
            long_description=open('README').read(),
            # Temp setting to prevent egg-ifying install, for ease of debugging
            zip_safe = False,
            classifiers=["Development Status :: 4 - Beta",
                         "Intended Audience :: Developers",
                         "License :: OSI Approved :: MIT License",
                         "Operating System :: OS Independent",
                         "Programming Language :: Python :: 2",
                         "Programming Language :: Python :: 2.5",
                         "Programming Language :: Python :: 2.6",
                         "Programming Language :: Python :: 2.7",
                         "Programming Language :: Python :: 3",
                         "Programming Language :: Python :: 3.2",
                         "Programming Language :: Python :: 3.3",
                         "Programming Language :: Python :: 3.4"
                     ])

# On Python 3, we need distribute (new setuptools) to do the 2to3 conversion
if sys.version_info >= (3,):
    from setuptools import setup
    args['use_2to3'] = True

setup(**args)
