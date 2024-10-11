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
__version__ = "3.3.1"
__author__ = "Brian M. Clapper"
__email__ = "bmc@clapper.org"
__url__ = "http://software.clapper.org/paragrep/"
__copyright__ = "1989-2023 Brian M. Clapper"
__license__ = "BSD-style license"

# Package stuff

__all__ = ["Paragrepper", "main"]

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import optparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional, Sequence as Seq, TextIO, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FULL_VERSION_STRING = (
    f"paragrep, Version {__version__}. " f"Copyright {__copyright__}"
)

DEFAULT_EOP_PATTERN = r"^\s*$"

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------


class ParagrepError(Exception):
    pass


class CommandLineError(Exception):
    pass


@dataclass
class Paragrepper:
    regexps: Seq[re.Pattern]
    files: Seq[str]
    eop_regexp: re.Pattern
    anding: bool
    case_blind: bool
    negate: bool
    print_eop: bool
    """
    Grep through a file, printing paragraphs that match one or more regular
    expressions.
    """

    def __post_init__(self):
        self._print_file_name = False
        self._print_file_header = False

    def grep(self):
        if len(self.files) == 0:
            found = self._search(sys.stdin)

        else:
            self._print_file_name = len(self.files) > 1
            found = False
            for file in self.files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        self._print_file_header = self._print_file_name
                        if self._search(f, filename=file):
                            found = True
                except IOError as e:
                    raise ParagrepError(f"""Can't open file "{file}": {e}""")

        return found

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def _search(self, f: TextIO, filename: Optional[str] = None) -> bool:
        paragraph = []
        last_empty = False
        found = False
        eop_line = None

        def print_paragraph(paragraph: Seq[str]) -> None:
            if self._print_file_header:
                print(f"::::::::::\n{filename}\n::::::::::\n")
                self._print_file_header = False
            print("\n".join(paragraph))
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

                if line[-1] == "\n":
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
                if line[-1] == "\n":
                    line = line[:-1]
                paragraph += [line]
                last_empty = False

        # We might have a paragraph left in the buffer. If so, search it.

        if not last_empty:
            if self._search_paragraph(paragraph):
                found = True
                print_paragraph(paragraph)

        return found

    def _search_paragraph(self, paragraph: Seq[str]) -> bool:
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


def _load_expr_files(files: Seq[str]) -> Seq[str]:
    result = []
    for file in files:
        try:
            with open(file) as f:
                for l in f.readlines():
                    result += [l.strip()]
        except IOError as e:
            raise ParagrepError(f"""Can't open file "{file}": {e}""")

    return result


def _parse_params(argv: Seq[str]) -> Tuple[optparse.Values, Seq[str]]:
    """
    Parse the command line arguments
    """

    prog = os.path.basename(argv[0])
    USAGE = f"""
{prog} [-iv] [-p EOP_REGEXP] regexp [file] ...
{prog} [-aiov] [-p EOP_REGEXP] [-e REGEXP] ... [-f EXP_FILE] ... [file] ...
{prog} -h | --help"""

    parser = optparse.OptionParser(usage=USAGE, version=FULL_VERSION_STRING)
    parser.add_option(
        "-a",
        "--and",
        action="store_true",
        dest="anding",
        help="Logically AND all regular expressions.",
    )
    parser.add_option(
        "-e",
        "--regexp",
        "--expr",
        action="append",
        dest="regexps",
        metavar="regexp",
        help="Specify a regular expression to find."
        "This option may be specified multiple times.",
    )
    parser.add_option(
        "-f",
        "--file",
        action="append",
        type="string",
        dest="exprFiles",
        metavar="exprfile",
        help="Specify a file full of regular expressions, " "one per line.",
    )
    parser.add_option(
        "-i",
        "--caseblind",
        action="store_true",
        dest="caseblind",
        help="Match without regard to case.",
    )
    parser.add_option(
        "-o",
        "--or",
        action="store_false",
        dest="anding",
        help="Logically OR all regular expressions.",
    )
    parser.add_option(
        "-p",
        "--eop",
        action="store",
        type="string",
        dest="eop_regexp",
        metavar="eop_regexp",
        default=DEFAULT_EOP_PATTERN,
        help=r"Specify an alternate regular expression "
        'to match end-of-paragraph. Defaults to "%(default)s".',
    )
    parser.add_option(
        "-P",
        "--print-eop",
        action="store_true",
        dest="print_eop",
        default=False,
        metavar="print_eop",
        help=r"Print the line that marks the end of each "
        "paragraph. Default: %default",
    )
    parser.add_option(
        "-v",
        "--negate",
        action="store_true",
        dest="negate",
        help="Negate the sense of the match.",
    )

    return parser.parse_args(argv)


def translate_args(options: optparse.Values, args: Seq[str]) -> Paragrepper:
    """
    Take the parsed command line options and arguments, and translate them
    into a Paragrepper object.

    Parameters:

    options - the options returned from an optparse.OptionParser's
              parse_args() call
    args    - the non-option arguments returned from an optparse.OptionParser's
              parse_args() call

    Returns: an instantiated Paragrepper object
    """
    try:
        # Figure out where to get the regular expressions to find.

        local_args: list[str] = list(args)
        uncompiled_regexps = []
        if options.regexps != None:
            uncompiled_regexps += options.regexps

        if options.exprFiles != None:
            uncompiled_regexps += _load_expr_files(options.exprFiles)

        # Try to compile the end-of-paragraph regular expression.
        eop_regexp = re.compile(options.eop_regexp)

        # Get the regular expressions to find.

        local_args = local_args[1:]
        if len(uncompiled_regexps) == 0:
            # No -e or -f seen. Use first non-option parameter.

            if len(local_args) == 0:
                raise CommandLineError("Not enough arguments.")

            uncompiled_regexps += [local_args[0]]
            del local_args[0]

        # Compile the regular expressions and save the compiled results.

        flags = re.IGNORECASE if options.caseblind else 0
        regexps: Seq[re.Pattern] = []
        for expr in uncompiled_regexps:
            regexps += [re.compile(pattern=expr, flags=flags)]

        # Are there any files, or are we searching standard input?

        files = []
        if len(local_args) > 0:
            files = local_args

        return Paragrepper(
            regexps=regexps,
            files=files,
            eop_regexp=eop_regexp,
            anding=options.anding,
            case_blind=options.caseblind,
            negate=options.negate,
            print_eop=options.print_eop,
        )
    except IOError as e:
        raise CommandLineError(str(e))
    except re.error as e:
        raise CommandLineError(
            f'Error in regular expression "{e.pattern}": {e}'
        )


def main() -> int:
    rc = 0

    try:
        options, args = _parse_params(sys.argv)
        p = translate_args(options, args)
        found = p.grep()
        if not found:
            rc = 1
    except CommandLineError as e:
        print(str(e), file=sys.stderr)
        rc = 1
    except ParagrepError as e:
        print(str(e), file=sys.stderr)
        rc = 1

    return rc


if __name__ == "__main__":
    sys.exit(main())
