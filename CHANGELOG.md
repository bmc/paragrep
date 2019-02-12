# Change log for paragrep

Version 3.2.0 (12 February, 2019)

- Starting with this version, `paragrep` will _only_ work on Python 3.6 or
  better.
- Added type annotations.
- Updated `print` statements to use f-strings.
- Removed dependency on `grizzled-python` library. This package now requires
  only the standard Python 3 library.

Version 3.1.2 (11 February, 2016)

- Updated dependency on `grizzled-python`, to pick up a version that's
  more compatible with Python 3.

Version 3.1.1 (13 August, 2012)

- Fixed installation download URL, allowing installs from `pip` to work again.

Version 3.1.0 (24 March, 2012)

- Added ability to display the matching end-of-paragraph lines. Specify
  the "-P" option. (Issue #1, https://github.com/bmc/paragrep/issues/1)
- "-a" and "-o" options not working correctly with multiple   regexs. Problem
  was a Python statement indentation issue. (Issue #2,
  https://github.com/bmc/paragrep/issues/2)
- Fixed some minor issues with the "-i" (case-blind) option
- Removed some dead code.


Version 3.0.7 (6 March, 2012)

- Removed unused "-t" option from option summary in usage message.


Version 3.0.6 (14 March, 2011)

- Removed setup.py dependency on ez_setup.
- Changed to refer to 'grizzled-python', instead of 'grizzled'


Version 3.0.5 (28 March, 2010)

- Updated to latest version of ez_setup.py
- Adjusted license to new BSD license.
- Changed URL to new GitHub URL.


Version 3.0.4 (16 January, 2009)

- Now reads lines from the files in a more memory-efficient manner.
- Fixed problem with compilation of regexps.


Version 3.0.3 (9 November, 2008)

- Version (--version) option is now handled by the option parser.
- Removed left-over camel case variable names.
- Fixed -i (case-blind) matching, which wasn't working.


Version 3.0.2 (3 September, 2008)

- Changed epydoc markup to use reStructuredText.
- Now properly matches anchored regular expressions (e.g., "^foo") against
  individual lines, rather than the entire paragraph as a whole.
- Added --version option.
- Now properly bundles ez_setup.py


Version 3.0.1 (20 May, 2008)

- Updated to correspond to changes in the dependent Grizzled API.


Version 3.0 (3 April, 2008)

- Python version posted to the web. (Previous versions were implemented
  in Perl and C.)
