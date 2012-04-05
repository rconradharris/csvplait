========
csvplait
========

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

::

  $ cat script.csvplait
  read $FILENAME
  drop 0
  write $FILENAME.fixedup


  $ python csvplait.py script.csvplait FILENAME=sept.csv
