"""
paragrep - Paragraph Grep utility

**paragrep** is a paragraph grep utility. It searches for a series of regular
expressions in a text file (or several text files) and prints out the
paragraphs containing those expressions. Normally **paragrep** displays a
paragraph if it contains any of the expressions; this behavior can be modified
by using the `-a` option.

By default, a paragraph is defined as a block of text delimited by an empty or
blank line; this behavior can be altered with the `-p` option.

If no files are specified on the command line, **paragrep** searches
standard input.

This is the third implementation of **paragrep**. The first implementation,
in 1989, was in C. The second implementation, in 2003, was in perl. This is
the latest and greatest.

For help, run with `-h`.

For detailed documentation, see <http://software.clapper.org/paragrep/>

This software is released under a BSD license.
"""

# Info about the module
__version__   = '3.2.3'
__author__    = 'Brian M. Clapper'
__email__     = 'bmc@clapper.org'
__url__       = 'http://software.clapper.org/paragrep/'
__copyright__ = '1989-2023 Brian M. Clapper'
__license__   = 'BSD-style license'

# Package stuff

__all__     = ['Paragrepper', 'main']

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import os
import re
from typing import Sequence, Optional, TextIO, NoReturn

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FULL_VERSION_STRING = (f'paragrep, Version {__version__}. '
                       f'Copyright {__copyright__}')

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class ParagrepError(Exception):
    pass

class Paragrepper:
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

        self._print_file_name = False
        self._print_file_header = False

    def grep(self):
        if not self.files:
            found = self._search(sys.stdin)

        else:
            self._print_file_name = len(self.files) > 1
            found = False
            for file in self.files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        self._print_file_header = self._print_file_name
                        if self._search(f, filename=file):
                            found = True
                except IOError as e:
                    raise ParagrepError(f'''Can't open file "{file}": {e}''')

        return found


    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def _search(self, f: TextIO, filename: Optional[str] = None) -> bool:
        paragraph = []
        last_empty = False
        found = False
        eop_line = None

        def print_paragraph(paragraph: Sequence[str]) -> NoReturn:
            if self._print_file_header:
                print(f'::::::::::\n{filename}\n::::::::::\n')
                self._print_file_header = False
            print('\n'.join(paragraph))
            if self.print_eop and (eop_line is not None):
                print(eop_line)
            else:
                print()

        for line in f.readlines():
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

    def _search_paragraph(self, paragraph: Sequence[str]) -> bool:
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

def _load_expr_files(files: Sequence[str]) -> Sequence[str]:
    result = []
    for file in files:
        try:
            with open(file) as f:
                for l in f.readlines():
                    result += [l.strip()]
        except IOError as e:
            raise ParagrepError(f'''Can't open file "{file}": {e}''')

    return result

def _parse_params(paragrepper: Paragrepper, argv: Sequence[str]) -> None:
    # Parse the command-line parameters

    prog = os.path.basename(argv[0])
    USAGE = (
f'''
{prog} [-iv] [-p EOP_REGEXP] regexp [file] ...
{prog} [-aiov] [-p EOP_REGEXP] [-e REGEXP] ... [-f EXP_FILE] ... [file] ...
{prog} -h | --help'''
)

    import optparse
    parser = optparse.OptionParser(usage=USAGE, version=FULL_VERSION_STRING)
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
        except IOError as e:
            parser.error(e.message)

    # Try to compile the end-of-paragraph regular expression.

    try:
        paragrepper.eop_regexp = re.compile(options.eop_regexp)
    except Exception as e:
        parser.error(f'Bad regular expression "{options.eop_regexp}" to -p')

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
        except Exception as e:
            parser.error(f'Bad regular expression: "{expr}"')

    # Are there any files, or are we searching standard input?

    if len(args) > 0:
        paragrepper.files = args

def main() -> NoReturn:
    rc = 0
    p = Paragrepper()
    _parse_params(p, sys.argv)

    try:
        found = p.grep()
        if not found:
            rc = 1
    except ParagrepError as ex:
        print(str(ex), file=sys.stderr)
        rc = 1

    sys.exit(rc)


if __name__ == "__main__":
    main()
