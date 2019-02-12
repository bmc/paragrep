# paragrep, a paragraph _grep_

*paragrep* is a "paragraph grep" utility. It searches for a series of
regular expressions in a text file (or several text files) and prints out
the paragraphs containing those expressions. Normally paragrep displays a
paragraph if it contains any of the expressions; this behavior can be
modified by using the -a option.

## Quick Start

```
$ pip install paragrep
$ paragrep --help
```

**WARNING:** As of version 3.2.0, _paragrep_ no longer supports Python 2.
If you need to run it under Python 2, use an older version. e.g.:

```
$ pip install paragrep==3.1.3
```

## Complete docs

For all the docs, see the [project site](http://software.clapper.org/paragrep).
