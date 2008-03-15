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

# Parse through the script to get various values. Can't import it, 'cause it's
# a script without a ".py" extension.

reVersion = re.compile ("^__version__\s*=\s*\"([^\"]+)\"$")
reAuthor  = re.compile ("^__author__\s*=\s*\"([^,\"]+),\s*([^\"]+)\"$");
reURL     = re.compile ("^__url__\s*=\s*\"([^\"]+)\"$")
reLicense = re.compile ("^__license__\s*=\s*\"([^\"]+)\"$")

f = open ("paragrep.py")

VERSION = ""
AUTHOR  = ""
EMAIL   = ""
LICENSE = ""
URL     = ""

while 1:
    line = f.readline()
    if line == "":
        break

    m = reVersion.search (line)
    if m != None:
        VERSION = m.group (1)
        continue

    m = reAuthor.search (line)
    if m != None:
        (AUTHOR, EMAIL) = (m.group (1), m.group (2))
        continue

    m = reURL.search (line)
    if m != None:
        URL = m.group (1)
        continue

    m = reLicense.search (line)
    if m != None:
        LICENSE = m.group (1)
        continue

f.close()

# Now the setup stuff.

setup (name="paragrep",
       version=VERSION,
       description="Find and print paragraphs matching regular expressions",
       packages=find_packages(),
       url=URL,
       license=LICENSE,
       author=AUTHOR,
       author_email=EMAIL,
       entry_points = {'console_scripts' : 'paragrep=paragrep:main'})

