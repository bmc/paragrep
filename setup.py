#!/usr/bin/env python
#
# EasyInstall setup script for paragrep
#
# $Id$
# ---------------------------------------------------------------------------

import sys
import os
sys.path += [os.getcwd()]

import ez_setup
ez_setup.use_setuptools(download_delay=2)
from setuptools import setup, find_packages
import re
import imp

DESCRIPTION = "Print paragraphs matching regular expressions"

def load_info():
    # Look for identifiers beginning with "__" at the beginning of the line.

    result = {}
    pattern = re.compile(r'^(__\w+__)\s*=\s*[\'"]([^\'"]*)[\'"]')
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    for line in open(os.path.join(here, 'paragrep', '__init__.py'), 'r'):
        match = pattern.match(line)
        if match:
            result[match.group(1)] = match.group(2)

    sys.path = [here] + sys.path
    mf = os.path.join(here, 'paragrep', '__init__.py')
    try:
        m = imp.load_module('paragrep', open(mf), mf,
                            ('__init__.py', 'r', imp.PY_SOURCE))
        result['long_description'] = m.__doc__
    except:
        result['long_description'] = DESCRIPTION
    return result

info = load_info()

# Now the setup stuff.

setup (name             = 'paragrep',
       version          = info['__version__'],
       description      = DESCRIPTION,
       long_description = info['long_description'],
       packages         = find_packages(),
       py_modules       = ['ez_setup'],
       url              = info['__url__'],
       license          = info['__license__'],
       author           = info['__author__'],
       author_email     = info['__email__'],
       entry_points     = {'console_scripts' : 'paragrep=paragrep:main'},
       install_requires = ['grizzled>=0.8.1', ],
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
