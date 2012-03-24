#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
paragrep - Paragraph Grep utility

Usage
=====

**paragrep** [-aiov] [-p *eop_regexp*] [-e *regexp*] ... [-f *exp_file*] ... [*file* ] ...

**paragrep** [-iv] [-p *eop_regexp*] *regexp* [*file*] ...


Options
-------

  -a, --and                                   Logically *AND* all regular 
                                              expressions

  -e regexp, --regexp=regexp, --expr=regexp   Specify a regular expression 
                                              to find. This option may be
                                              specified multiple times.

  -f expr_file, --file=expr_file              Specify a file of regular
                                              expressions, one per line.

  -h, --help                                  Show this message and exit

  -i, --caseblind                             Match without regard to case

  -o, --or                                    Logically *OR* all regular 
                                              expressions

  -p eop_regexp, --eop=eop_regexp             Specify an alternate regular
                                              expression to match the end
                                              of a paragraph. Default: 
                                              ``^\s*$``

  -v, --negate                                Negate the sense of the match.
  
  --version                                   Display version and exit.

Description
===========

**paragrep** is a paragraph grep utility. It searches for a series of regular
expressions in a text file (or several text files) and prints out the
paragraphs containing those expressions. Normally **paragrep** displays a
paragraph if it contains any of the expressions; this behavior can be modified
by using the ``-a`` option.

By default, a paragraph is defined as a block of text delimited by an empty or
blank line; this behavior can be altered with the ``-p`` option.

If no files are specified on the command line, **paragrep** searches
standard input.

This is the third implementation of **paragrep**. The first implementation,
in 1989, was in C. The second implementation, in 2003, was in perl. This is
the latest and greatest.

Options in Detail
-----------------

``-a``
~~~~~~~

The *and* option: Only display a paragraph if it contains *all* the regular
expressions specified. The default is to display a paragraph if it contains
*any* of the regular expressions. See the ``-o`` option, below.

``-e`` *expression*
~~~~~~~~~~~~~~~~~~~

Adds a regular expression to the set of expressions to use when matching
paragraphs. More than one ``-e`` argument may be specified. If there's only
one expression, the ``-e`` may be omitted for brevity. (Think *sed*.)

``-f`` *expfile*
~~~~~~~~~~~~~~~~

Specifies a file containing regular expressions, one expression per line.
Each expression in the file is added to the set of expression against which
paragraphs are to be matched.   More than one ``-f`` argument is permitted.
Also, ``-f`` and ``-e`` may be specified together.

``-i``
~~~~~~

Considers upper- and lower-case letters to be identical when making comparisons.

``-o``
~~~~~~

The *or* option: Display a paragraph if it contains *any* the regular
expressions specified. Since this option is the default, it is rarely
specified on the command line. It exists primarily to negate the effect of a
previous ``-a`` option. (e.g., If you've defined an alias for **paragrep**
that specifies the ``-a`` option, ``-o`` would be necessary to force the *or*
behavior.)

``-p`` *eop_expression*
~~~~~~~~~~~~~~~~~~~~~~~

Specifies a regular expression to be used match paragraph delimiters.  Any
line that matches this regular expression is assumed to delimit paragraphs
without actually being part of a paragraph (i.e., lines matching this
expression are never printed).  If this option is not specified, it
defaults to::

    ^[ \\t]*$

which matches blank or empty lines. (``\\\\t`` represents the horizontal tab
character. If you need to specify a horizontal tab, you'll need to type the
actual character; **paragrep** doesn't recognize C-style metacharacters.)

``-v``
~~~~~~

Displays all lines that do not match specified expressions. The negation logic
works on DeMorgan's Laws. Normally, if ``-a`` is specified, **paragrep** uses
the following logic to match the paragraph::

    match = contains(expr1) AND contains(expr2) ...

Specifying ``-v`` along with ``-a`` changes this logic to::

    match = lacks(expr1) OR lacks(expr2) ...

Likewise, without ``-a`` or ``-v`` (i.e., using ``-o``, which is the default),
the matching logic is::

    match = contains(expr1) OR contains(expr2) ...

Negating that logic with ``-v`` causes paragrep to match paragraphs with::

    match = lacks(expr1) AND lacks(expr2) ...

See Also
========

 - The Unix *grep* command
 - The Python ``re`` module (http://docs.python.org/lib/module-re.html)

Copyright and License
=====================

Copyright (c) 1989-2012 Brian M. Clapper
All rights reserved.

This software is released under a BSD license, adapted from
http://opensource.org/licenses/bsd-license.php

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

- Neither the names "clapper.org", "paragrep", nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import with_statement

__docformat__ = 'restructuredtext'

# Info about the module
__version__   = '3.1.1'
__author__    = 'Brian M. Clapper'
__email__     = 'bmc@clapper.org'
__url__       = 'http://software.clapper.org/paragrep/'
__copyright__ = '1989-2012 Brian M. Clapper'
__license__   = 'BSD-style license'

# Package stuff

__all__     = ['Paragrepper', 'main']

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import string
import sys
import os
import re

from grizzled.cmdline import CommandLineParser
from grizzled.exception import ExceptionWithMessage

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FULL_VERSION_STRING = 'paragrep, Version %s. Copyright %s' %\
                    (__version__, __copyright__)

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class ParagrepError(ExceptionWithMessage):
    pass

class Paragrepper(object):
    """
    Grep through a file, printing paragraphs that match one or more regular
    expressions.
    """
    def __init__(self):
        self.regexps = []
        self.files = None
        self.eop_regexp = None
        self.anding = False
        self.case_blind = False
        self.negate = False
        self.show_version = False
        self.print_eop = False

        self.__print_file_name = False
        self.__print_file_header = False

    def grep(self):
        if not self.files:
            found = self._search(sys.stdin)

        else:
            self.__print_file_name = len(self.files) > 1
            found = False
            for file in self.files:
                try:
                    with open(file) as f:
                        self.__print_file_header = self.__print_file_name
                        if self._search(f, filename=file):
                            found = True
                except IOError, (err, msg):
                    raise ParagrepError("Can't open file \"%s\": %s" %
                                        (file, msg))

        return found


    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def _search(self, f, filename=None):
        paragraph = []
        last_empty = False
        found = False
        eop_line = None

        def print_paragraph(paragraph):
            if self.__print_file_header:
                print '::::::::::\n%s\n::::::::::\n' % filename
                self.__print_file_header = False
            print '\n'.join(paragraph)
            if self.print_eop and (eop_line is not None):
                print eop_line
            else:
                print ""

        for line in f:
            if self.eop_regexp.match(line):
                # End of current paragraph, or a redundent (consecutive)
                # end-of-paragraph mark.  If it's truly the first one since
                # the end of the paragraph, search the accumulated lines of
                # the paragraph.

                if line[-1] == '\n':
                    eop_line = line[:-1]
                else:
                    eop_line = line

                if not last_empty:
                    last_empty = True
                    found = self._search_paragraph(paragraph)
                    if found:
                        print_paragraph(paragraph)
                    paragraph = []

            else:
                # Save this line in the current paragraph buffer
                if line[-1] == '\n':
                    line = line[:-1]
                paragraph += [line]
                last_empty = False

        # We might have a paragraph left in the buffer. If so, search it.

        if not last_empty:
            if self._search_paragraph(paragraph):
                found = True
                print_paragraph(paragraph)

        return found

    def _search_paragraph(self, paragraph):
        found_count_must_be = 1
        if self.anding:
            # If ANDing, must match ALL the regular expressions.
            found_count_must_be = len(self.regexps)

        total_found = 0
        for re in self.regexps:
            for line in paragraph:
                if re.search(line):
                    total_found += 1
                    break

        if (not self.negate) and (total_found >= found_count_must_be):
            found = True
        elif self.negate and (total_found != found_count_must_be):
            found = True
        else:
            found = False

        return found

# ---------------------------------------------------------------------------
# Main Program
# ---------------------------------------------------------------------------

def _load_expr_files(files):
    result = []
    for file in files:
        try:
            with open(file) as f:
                for l in f.readlines():
                    result += [l.strip()]
        except IOError:
            raise ParagrepError("Can't open file \"%s\": %s" % (file, msg))

    return result

def _parse_params(paragrepper, argv):
    # Parse the command-line parameters

    prog = os.path.basename(argv[0])
    USAGE = \
'\n' \
'%s [-aiov] [-p EOP_REGEXP] [-e REGEXP] ... [-f EXP_FILE] ... [file] ...\n' \
'               -OR-\n' \
'%s [-iv] [-p EOP_REGEXP] regexp [file] ...' % (prog, prog)

    parser = CommandLineParser(usage=USAGE, version=FULL_VERSION_STRING)
    parser.add_option('-a', '--and', action='store_true', dest='anding',
                      help='Logically AND all regular expressions.')
    parser.add_option('-e', '--regexp', '--expr', action='append',
                      dest='regexps', metavar='regexp',
                      help='Specify a regular expression to find.' \
                      'This option may be specified multiple times.')
    parser.add_option('-f', '--file', action='append', type='string',
                      dest='exprFiles', metavar='exprfile',
                      help='Specify a file full of regular expressions, ' \
                      'one per line.')
    parser.add_option('-i', '--caseblind', action='store_true',
                      dest='caseblind',
                      help='Match without regard to case.')
    parser.add_option('-o', '--or', action='store_false', dest='anding',
                      help='Logically OR all regular expressions.')
    parser.add_option('-p', '--eop', action='store', type='string',
                      dest='eop_regexp', default=r'^\s*$', metavar='eop_regexp',
                      help=r'Specify an alternate regular expression ' \
                      'to match end-of-paragraph. Default: %default')
    parser.add_option('-P', '--print-eop', action='store_true',
                      dest='print_eop', default=False, metavar='print_eop',
                      help=r'Print the line that marks the end of each ' \
                      'paragraph. Default: %default')
    parser.add_option('-v', '--negate', action='store_true', dest='negate',
                      help='Negate the sense of the match.')

    (options, args) = parser.parse_args(argv)

    # Save the flag options

    paragrepper.anding = options.anding
    paragrepper.case_blind = options.caseblind
    paragrepper.negate = options.negate
    paragrepper.print_eop = options.print_eop

    # Figure out where to get the regular expressions to find.

    uncompiled_regexps = []
    if options.regexps != None:
        uncompiled_regexps += options.regexps

    if options.exprFiles != None:
        try:
            uncompiled_regexps += _load_expr_files(options.exprFiles)
        except IOError, (errno, msg):
            parser.error(msg)

    # Try to compile the end-of-paragraph regular expression.

    try:
        paragrepper.eop_regexp = re.compile(options.eop_regexp)
    except Exception, msg:
        parser.error('Bad regular expression "%s" to -p option' % \
                     options.eop_regexp)

    args = args[1:]
    if len(uncompiled_regexps) == 0:
        # No -e or -f seen. Use first non-option parameter.

        try:
            uncompiled_regexps += [args[0]]
            del args[0]
        except IndexError:
            parser.error('Not enough arguments.')

    # Compile the regular expressions and save the compiled results.

    flags = re.IGNORECASE if paragrepper.case_blind else None
    for expr in uncompiled_regexps:
        try:
            if flags:
                re_args = (expr, flags)
            else:
                re_args = (expr,)
            paragrepper.regexps += [re.compile(*re_args)]
        except Exception, msg:
            parser.error('Bad regular expression: "%s"' % expr)

    # Are there any files, or are we searching standard input?

    if len(args) > 0:
        paragrepper.files = args

def main():

    rc = 0
    p = Paragrepper()
    _parse_params(p, sys.argv)
    try:
        found = p.grep()
        if not found:
            rc = 1
    except ParagrepError, ex:
        print >> sys.stderr, ex.message
        rc = 1

    sys.exit(rc)


if __name__ == "__main__":
    main()
