#!/usr/bin/env python
#
# Distutils setup script for rsscheck
#
# $Id$
# ---------------------------------------------------------------------------

import ez_setup
ez_setup.use_setuptools(download_delay=2)
from setuptools import setup, find_packages
import re
import sys
import os

#sys.path += [os.getcwd()]

import paragrep
print paragrep.__version__

# Now the setup stuff.

setup (name="paragrep",
       version=paragrep.__version__,
       description="Find and print paragraphs matching regular expressions",
       packages=find_packages(),
       url=paragrep.__url__,
       license=paragrep.__license__,
       author=paragrep.__author__,
       author_email=paragrep.__email__,
       entry_points = {'console_scripts' : 'paragrep=paragrep:main'})

