#!/usr/bin/env python
#
# EasyInstall setup script for paragrep
#
# $Id$
# ---------------------------------------------------------------------------

import ez_setup
ez_setup.use_setuptools(download_delay=2)
from setuptools import setup, find_packages
import re
import sys
import os

def loadInfo():
    # Look for identifiers beginning with "__" at the beginning of the line.

    result = {}
    pattern = re.compile(r'^(__\w+__)\s*=\s*[\'"]([^\'"]*)[\'"]')
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    for line in open(os.path.join(here, 'paragrep', '__init__.py'), 'r'):
        match = pattern.match(line)
        if match:
            result[match.group(1)] = match.group(2)
    return result

info = loadInfo()

# Now the setup stuff.

setup (name          = 'paragrep',
       version       = info['__version__'],
       description   = "Find and print paragraphs matching regular expressions",
       packages      = find_packages(),
       url           = info['__url__'],
       license       = info['__license__'],
       author        = info['__author__'],
       author_email  = info['__email__'],
       entry_points  = {'console_scripts' : 'paragrep=paragrep:main'},
       data_files    = [('man', ['man/paragrep.1'])]
)
