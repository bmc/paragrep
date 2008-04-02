#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
paragrep - Paragraph Grep utility

Usage
=====

B{paragrep} [-aiotv] [-p I{eop_regexp}] [-e I{regexp}] ... [-f I{exp_file}] ... [I{file} ] ... 

B{paragrep} [-itv] [-p I{eop_regexp}] I{regexp} [I{file}] ...


Options
-------

Summary of options::

    -h, --help            Show this message and exit.

    -a, --and             Logically AND all regular expressions.

    -o, --or              Logically OR all regular expressions.

    -i, --caseblind       Match without regard to case.

    -v, --negate          Negate the sense of the match.

    -e regexp             Specify a regular expression to find.This option may
    --regexp=regexp       be specified multiple times.
    --expr=regexp
                      
    -p eop_regexp         Specify an alternate regular expression to match end-
    --eop=eop_regexp      of-paragraph. Default: ^\s*$
                      
    -f expr_file          Specify a file full of regular expressions, one per
    --file=expr_file      line.


Description
===========

B{paragrep} is a paragraph grep utility. It searches for a series of
regular expressions in a text file (or several text files) and prints out
the paragraphs containing those expressions. Normally B{paragrep} displays
a paragraph if it contains any of the expressions; this behavior can be
modified by using the C{-a} option.

By default, a paragraph is defined as a block of text delimited by an empty
or blank line; this behavior can be altered with the C{-p} option.

If no files are specified on the command line, B{paragrep} searches
standard input.

This is the third implementation of B{paragrep}. The first implementation,
in 1989, was in C. The second implementation, in 2003, was in perl. This is
the latest and greatest.

Options in Detail
-----------------

C{-a}
~~~~~

The I{and} option: Only display a paragraph if it contains I{all} the
regular expressions specified. The default is to display a paragraph if
it contains I{any} of the regular expressions. See the C{-o} option, below.

C{-e} I{expression}
~~~~~~~~~~~~~~~~~~~

Adds a regular expression to the set of expressions to use when matching
paragraphs. More than one C{-e} argument may be specified. If there's only
one expression, the C{-e} may be omitted for brevity. (Think I{sed}.)

C{-f} I{expfile}
~~~~~~~~~~~~~~~~

Specifies a file containing regular expressions, one expression per line.
Each expression in the file is added to the set of expression against which
paragraphs are to be matched.   More than one C{-f} argument is permitted.
Also, C{-f} and C{-e} may be specified together.

C{-i}
~~~~~

Considers upper- and lower-case letters to be identical when making comparisons.

C{-o}
~~~~~

The I{or} option: Display a paragraph if it contains I{any} the
regular expressions specified. Since this option is the default, it is
rarely specified on the command line. It exists primarily to negate the
effect of a previous C{-a} option. (e.g., If you've defined an alias for
B{paragrep} that specifies the C{-a} option, C{-o} would be necessary to
force the I{or} behavior.)

C{-p} I{eop_expression}
~~~~~~~~~~~~~~~~~~~~~~~

Specifies a regular expression to be used match paragraph delimiters.  Any
line that matches this regular expression is assumed to delimit paragraphs
without actually being part of a paragraph (i.e., lines matching this
expression are never printed).  If this option is not specified, it
defaults to::

    ^[ \\t]*$

which matches blank or empty lines. (C{\\t} represents the horizontal tab
character. If you need to specify a horizontal tab, you'll need to type the
actual character; B{paragrep} doesn't recognize C-style metacharacters.)

C{-v}
~~~~~

Displays all lines that do not match specified expressions.  The negation
logic works on DeMorgan's Laws.  Normally, if C{-a} is specified,
B{paragrep} uses the following logic to match the paragraph::

    match = contains(expr1) AND contains(expr2) ... 

Specifying C{-v} along with C{-a} changes this logic to::

    match = lacks(expr1) OR lacks(expr2) ...

Likewise, without C{-a} or C{-v} (i.e., using C{-o}, which is the default),
the matching logic is::

    match = contains(expr1) OR contains(expr2) ... 

Negating that logic with C{-v} causes paragrep to match paragraphs with::

    match = lacks(expr1) AND lacks(expr2) ... 

See Also
========

 - The Unix I{grep}(1) command
 - The Python U{C{re} module<http://docs.python.org/lib/module-re.html>}

Copyright and License
=====================

Copyright © 1989-2008 Brian M. Clapper

This is free software, released under the following BSD-like license:

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 - Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

 - The end-user documentation included with the redistribution, if any,
   must include the following acknowlegement:

   This product includes software developed by Brian M. Clapper
   (bmc@clapper.org, http://www.clapper.org/bmc/). That software is
   copyright \169 2008 Brian M. Clapper.

   Alternately, this acknowlegement may appear in the software itself, if
   and wherever such third-party acknowlegements normally appear.

THIS SOFTWARE IS PROVIDED B{AS IS} AND ANY EXPRESSED OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL BRIAN M. CLAPPER BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
"""

# $Id$

# Info about the module
__version__   = '3.0'
__author__    = 'Brian Clapper'
__email__     = 'bmc@clapper.org'
__url__       = 'http://www.clapper.org/software/python/paragrep/'
__copyright__ = '1989-2008 Brian M. Clapper'
__license__   = 'BSD-style license'

# Package stuff

__all__     = ['Paragrepper', 'main']

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from grizzled.optparser import CommandLineParser
import string
import sys
import os
import re

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class Paragrepper(object):
    """
    Grep through a file, printing paragraphs that match one or more regular
    expressions.
    """
    def __init__(self):
        self.regexps = []
        self.files = None
        self.eopRegexp = None
        self.anding = False
        self.caseBlind = False
        self.negate = False

        self.__printFileName = False
        self.__printFileHeader = False

    def grep(self):
        if not self.files:
            found = self.__search(sys.stdin)

        else:
            self.__printFileName = len(self.files) > 1
            found = False
            for file in self.files:
                f = open(file)
                self.__printFileHeader = self.__printFileName
                if self.__search(f, filename=file):
                    found = True
                f.close()

        return found
            

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def __search(self, f, filename=None):
        paragraph = []
        last_empty = False
        found = False

        for line in f.readlines():
            if self.eopRegexp.match(line):
		# End of current paragraph, or a redundent (consecutive)
		# end-of-paragraph mark.  If it's truly the first one since
		# the end of the paragraph, search the accumulated lines of
		# the paragraph.

                if not last_empty:
                    last_empty = True
                    found = self.__searchParagraph(paragraph, filename)
                    paragraph = []

            else:
                # Save this line in the current paragraph buffer

                if line[-1] == '\n':
                    line = line[:-1]
                paragraph += [line]
                last_empty = False

        # We might have a paragraph left in the buffer. If so, search it.

        if not last_empty:
            found = self.__searchParagraph(paragraph, filename)

        return found

    def __searchParagraph(self, paragraph, filename):
        found_count_must_be = 1
        if self.anding:
            # If ANDing, must match ALL the regular expressions.

            found_count_must_be = len(self.regexps)

        paragraph_as_one_string = ' '.join(paragraph)
        if self.caseBlind:
            paragraph_as_one_string = paragraph_as_one_string.lower()

        total_found = 0
        for re in self.regexps:
            if re.search(paragraph_as_one_string):
                total_found += 1

            if total_found == found_count_must_be:
                break

        if ((total_found == found_count_must_be) and (not self.negate)) or \
           ((total_found != found_count_must_be) and self.negate):
            found = True
            if self.__printFileHeader:
                print '::::::::::\n%s\n::::::::::\n' % filename
                self.__printFileHeader = False
            print '\n'.join(paragraph) + '\n'
        else:
            found = False

        return found

# ---------------------------------------------------------------------------
# Main Program
# ---------------------------------------------------------------------------

def __loadExprFiles(files):
    result = []
    for file in files:
        try:
            f = open(file)
        except IOError, (err, msg):
            raise IOError, (err, "Can't open file \"%s\": %s" % (file, msg))

        for l in f.readlines():
            result += [l.strip()]
        f.close()
    return result

def __parseParams(paragrepper, argv):
    # Parse the command-line parameters

    prog = os.path.basename(argv[0])
    USAGE = \
'\n' \
'%s [-aiotv] [-p EOP_REGEXP] [-e REGEXP] ... [-f EXP_FILE] ... [file] ...\n' \
'               -OR-\n' \
'%s [-itv] [-p EOP_REGEXP] regexp [file] ...' % (prog, prog)

    parser = CommandLineParser(usage=USAGE)
    parser.addOption('-a', '--and', action='store_true', dest='anding',
                     help='Logically AND all regular expressions.')
    parser.addOption('-o', '--or', action='store_false', dest='anding',
                     help='Logically OR all regular expressions.')
    parser.addOption('-i', '--caseblind', action='store_true',
                     dest='caseblind',
                     help='Match without regard to case.')
    parser.addOption('-v', '--negate', action='store_true', dest='negate',
                     help='Negate the sense of the match.')
    parser.addOption('-e', '--regexp', '--expr', action='append',
                     dest='regexps',
                     help='Specify a regular expression to find.' \
                     'This option may be specified multiple times.')
    parser.addOption('-p', '--eop', action='store', type='string',
                     dest='eop_regexp', default=r'^\s*$',
                     help=r'Specify an alternate regular expression ' \
                     'to match end-of-paragraph. Default: %default')
    parser.addOption('-f', '--file', action='append', type='string',
                     dest='exprFiles',
                     help='Specify a file full of regular expressions, ' \
                     'one per line.')

    (options, args) = parser.parseArgs(argv)

    # Save the flag options

    paragrepper.anding = options.anding
    paragrepper.caseBlind = options.caseblind
    paragrepper.negate = options.negate

    # Figure out where to get the regular expressions to find.

    uncompiledRegexps = []
    if options.regexps != None:
        uncompiledRegexps += options.regexps

    if options.exprFiles != None:
        try:
            uncompiledRegexps += __loadExprFiles(options.exprFiles)
        except IOError, (errno, msg):
            parser.error(msg)

    # Try to compile the end-of-paragraph regular expression.

    try:
        paragrepper.eopRegexp = re.compile(options.eop_regexp)
    except Exception, msg:
        parser.error('Bad regular expression "%s" to -p option' % \
                     options.eop_regexp)

    args = args[1:]
    if len(uncompiledRegexps) == 0:
        # No -e or -f seen. Use first non-option parameter.

        try:
            uncompiledRegexps += [args[0]]
            del args[0]
        except IndexError:
            parser.error('Not enough arguments.')

    # Compile the regular expressions and save the compiled results.

    for expr in uncompiledRegexps:
        try:
            paragrepper.regexps += [re.compile(expr)]
        except Exception, msg:
            parser.error('Bad regular expression: "%s"' % expr)

    # Are there any files, or are we searching standard input?

    if len(args) > 0:
        paragrepper.files = args

def main():

    p = Paragrepper()
    __parseParams(p, sys.argv)
    found = p.grep()
    if found:
        rc = 0
    else:
        rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
