#!/usr/bin/env python

import sys
import os

sys.path += [os.getcwd()]

from setuptools import setup, find_packages

DESCRIPTION = "Print paragraphs matching regular expressions"

if sys.version_info[0:2] < (3, 6):
    msg = ('As of version 3.2.0, the paragrep package no longer supports ' +
           'Python 2. Either upgrade to Python 3.6 or better, or use an ' +
           'older version of paragrep (e.g., 3.1.3).')
    sys.stderr.write(msg + '\n')
    raise Exception(msg)

def import_from_file(file, name):
    # See https://stackoverflow.com/a/19011259/53495
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader(name, file)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

here = os.getcwd()
paragrep = import_from_file(os.path.join(here, 'paragrep', '__init__.py'),
                            'paragrep')

NAME = 'paragrep'

# Now the setup stuff.

setup (name             = NAME,
       version          = paragrep.__version__,
       description      = DESCRIPTION,
       long_description = paragrep.__doc__,
       packages         = find_packages(),
       url              = paragrep.__url__,
       license          = paragrep.__license__,
       author           = paragrep.__author__,
       author_email     = paragrep.__email__,
       entry_points     = {'console_scripts' : 'paragrep=paragrep:main'},
       install_requires = [],
       data_files       = [('man', ['man/paragrep.1'])],
       classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
       ]
)
