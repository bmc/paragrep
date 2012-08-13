---
title: paragrep, a paragraph grep tool
layout: withTOC
---

## Introduction

*paragrep* is a "paragraph grep" utility. It searches for a series of
regular expressions in a text file (or several text files) and prints out
the paragraphs containing those expressions. Normally paragrep displays a
paragraph if it contains any of the expressions; this behavior can be
modified by using the -a option.

By default, a paragraph is defined as a block of text delimited by an empty
or blank line; this behavior can be altered with the `-p` option.

If no files are specified on the command line, *paragrep* searches standard
input.

## Installation

The easiest way to install *paragrep* is via [pip][] or [EasyInstall][]. Use
one of the following commands:

    $ pip install paragrep
    $ easy_install paragrep

If you'd prefer to install from source, you can either:

* Download and unpack the code from the [Downloads][] page
* Use `git clone git://github.com/bmc/paragrep.git` to pull down the source
  repository.

Then, within the resulting `paragrep` directory, type:

    $ python setup.py install

[pip]: http://www.pip-installer.org/
[EasyInstall]: http://pypi.python.org/pypi/setuptools
[Downloads]: https://github.com/bmc/paragrep/downloads
[GitHub repo]: https://github.com/bmc/paragrep/

## Usage

> paragrep \[-aiotv\] \[-p *regexp*\] \[-e *regexp*\] ... \[-f *exprfile*\] ... \[*file*\] ...

> paragrep \[-itv\] \[-p eop_regexp\] regexp \[file\] ...

### Options, in brief

* `-a`, `--and`: Logically *and* all regular expressions
* `-e regexp`, `--expr=regexp`, `--regexp=regexp`: Specify a regular expression
  to find. This option may be specified multiple times.
* `-f exprfile`, `--file=exprfile`: Specify a file containing regular 
  expressions to find, with one expression per line.
* `-h`, `--help`: Print the usage message and exit.
* `-o`, `--or`: Logically *or* all regular expressions.
* `-p regexp`, `--eop=regexp`: Specify an alternate regular expression to
  match lines that indicate paragraph breaks. By default, this value is
  `^\s*$`
* `-v`, `--negate`: Negate the sense of the match.
* `--version`: Display the version and exit.

### Options, in detail

#### `-a`

`-a` is the *and* option. It only displays paragraphs that contain *all*
the regular expressions specified on the command line. The default is to
display paragraphs that contain *any* of the regular expressions. (See `-o`.)

#### `-e`

Adds a regular expression to the set of expressions to use when matching
paragraphs. More than one `-e` argument may be specified. If there's only
one expression, the `-e` may be omitted for brevity. (Think *sed*.)

#### `-f`

`-f expfile` specifies a file containing regular expressions, one
expression per line. Each expression in the file is added to the set of
expression against which paragraphs are to be matched. More than one `-f`
argument is permitted. Also, `-f` and `-e` may be specified together.

#### `-i`

Specifies case-blind pattern matching. The default is case-sensitive pattern
matching.

#### `-o`

`-o` is the *or* option. It displays a paragraph if it contains *any* the
regular expressions specified. Since this option is the default, it is
rarely specified on the command line. It exists primarily to negate the
effect of a previous -a option. (e.g., If you've defined an alias for
*paragrep* that specifies the `-a` option, `-o` would be necessary to force
the *or* behavior.)

#### `-p`

Specifies a regular expression to be used match paragraph delimiters. Any
line that matches this regular expression is assumed to delimit paragraphs
without actually being part of a paragraph (i.e., lines matching this
expression are never printed). If this option is not specified, it defaults
to:

    ^[ \t]*$

which matches blank or empty lines. (`\t` represents the horizontal tab
character. If you need to specify a horizontal tab, you'll need to type the
actual character; *paragrep* doesn't recognize C-style metacharacters.)

#### `-P`

Displays the lines that mark the end of each paragraph, instead of separating
matching paragraphs with a newline (which is the default).

#### `-v`

Displays all lines that do not match specified expressions. The negation
logic works on [De Morgan's laws][]. Normally, if `-a` is specified,
*paragrep* uses the following logic to match the paragraph:

    match = contains(expr1) AND contains(expr2) ...

Specifying `-v` along with `-a` changes this logic to:

    match = lacks(expr1) OR lacks(expr2) ...

Likewise, without `-a` or `-v` (i.e., using `-o`, which is the default),
the matching logic is:

    match = contains(expr1) OR contains(expr2) ...

Negating that logic with `-v` causes paragrep to match paragraphs with:

    match = lacks(expr1) AND lacks(expr2) ...

## Getting and installing *paragrep*

### Installing via pip

Because *paragrep* is available via [PyPI][], if you have [pip][]
installed on your system, installing *paragrep* is as easy as running this
command (usually as `root` or the system administrator):

    pip install paragrep

### Installing from source

You can also install *paragrep* from source. Either download the source (as
a zip or tarball) from <http://github.com/bmc/paragrep/downloads>, or make
a local read-only clone of the [GitHub repository][] using one of the
following commands:

    $ git clone git://github.com/bmc/paragrep.git
    $ git clone http://github.com/bmc/paragrep.git

Once you have a local `paragrep` source directory, change your working directory
to the source directory, and type:

    python setup.py install

To install it somewhere other than the default location (such as in your
home directory) type:

    python setup.py install --prefix=$HOME

## Trivia

This is the third implementation of *paragrep*. The first implementation, in
1989, was in C. The second implementation, in 2003, was in [Perl][]. This is
the latest and greatest.


## Author

[Brian M. Clapper][]

## Copyright

Copyright &copy; 1998-2011 Brian M. Clapper

## License

[BSD license][].

## Change log

You can find the change log [here](https://github.com/bmc/paragrep/blob/master/CHANGELOG.md).

## Patches

I gladly accept patches from their original authors. Feel free to email
patches to me or to fork the [GitHub repository][] and send me a pull
request. Along with any patch you send:

* Please state that the patch is your original work.
* Please indicate that you license the work to the Paragrep project
  under a [BSD License][].


[BSD license]: license.html
[GitHub repository]: http://github.com/bmc/paragrep
[De Morgan's laws]: http://en.wikipedia.org/wiki/De_Morgan's_laws
[PyPI]: http://pypi.python.org/pypi
[Perl]: http://www.perl.org/
[Brian M. Clapper]: mailto:bmc@clapper.org
[pip]: http://pip-installer.org/
