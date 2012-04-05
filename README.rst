========
csvplait
========

csvplait is a tool for manipulating CSV files either interactively or via
script.

Usage
=====

Interactive
-----------

::

  $ python csvplait.py

    # Read in the CSV
    > read myfile.csv

    # Pretty print the table
    > pp

    # Drop first 2 columns
    > drop 0 1

    # Keep first five columns (labeled 0 to 4)
    > slice 0 4

    # this -> This
    > titleize 0

    # foo -> bar
    > strsub foo bar 0 2

    > write fixedup.csv


Script
------

You can easily create a script by writing out your history to a file::

  > history script.csvplait

If you want to make your script even more programatic, you can add variables
using a bash-like syntax::

  $ cat script.csvplait
  read $FILENAME
  drop 0
  write $FILENAME.fixedup


Then, to invoke the script, run `csvplait` with the script as an argument as
well as any environment variables that the script uses::

  $ python csvplait.py script.csvplait FILENAME=sept.csv
