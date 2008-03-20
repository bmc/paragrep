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
import paragrep

# Now the setup stuff.

setup (name          = "paragrep",
       version       = paragrep.__version__,
       description   = "Find and print paragraphs matching regular expressions",
       packages      = find_packages(),
       url           = paragrep.__url__,
       license       = paragrep.__license__,
       author        = paragrep.__author__,
       author_email  = paragrep.__email__,
       entry_points  = {'console_scripts' : 'paragrep=paragrep:main'},
       data_files    = [('man', ['docs/paragrep.1'])]
)

