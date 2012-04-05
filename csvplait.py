"""
csvplait.py - Interactive Tool for Manipulating CSV files

Copyright (c) 2012 Rick Harris <rconradharris[AT]gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""
import cmd
import csv as csv_module
import datetime
import functools
import re
import shlex
import sys

import prettytable


def apostrophe_safe_title(s):
    """Like `str.title` but handles apostrophes

    see http://bugs.python.org/issue7008
    """
    return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), s.title())


def inplace_slice(L, start, end):
    del L[:start]
    del L[end:]


def inplace_reorder(L, order):
    orig_len = len(L)
    for i in order:
        L.append(L[i])
    del L[:orig_len]


def clipstr(s, width=None):
    if width is not None and len(s) > width:
        s = s[:width] + '...'
    return s


class CSV(object):
    def __init__(self):
        self.col_headings = None
        self.rows = []
        self.num_cols = 0

    def set_headings(self, col_headings=None):
        self.col_headings = col_headings or self.rows.pop(0)

    def pad_columns(self, padding=""):
        for row in self.rows:
            deficit = self.num_cols - len(row)
            if deficit:
                row.extend([padding] * deficit)

    def pretty_print(self, stdout=None):
        if self.col_headings:
            headings = ['%d: %s' % (idx, heading) for idx, heading in
                        enumerate(self.col_headings)]
        else:
            headings = map(str, range(self.num_cols))

        table = prettytable.PrettyTable(headings)
        clip_field = functools.partial(clipstr, width=25)
        for row in self.rows:
            row = map(clip_field, row)
            table.add_row(row)

        if stdout:
            stdout.write(str(table))
        else:
            print table

    def read(self, filename):
        with open(filename, 'r') as f:
            self.readfp(f)

    def readfp(self, fp):
        self.num_cols = 0
        self.rows = []

        for row in csv_module.reader(fp):
            if len(row) > self.num_cols:
                self.num_cols = len(row)
            self.rows.append(row)

        self.col_headings = None

    def writefp(self, fp):
        writer = csv_module.writer(fp)

        if self.col_headings:
            writer.writerow(self.col_headings)

        writer.writerows(self.rows)

    def write(self, filename=None):
        if filename:
            with open(filename, 'wb') as f:
                self.writefp(f)
        else:
            self.writefp(sys.stdout)

    def slice_columns(self, start_col, end_col):
        for row in self.rows:
            inplace_slice(row, start_col, end_col + 1)

        if self.col_headings:
            inplace_slice(self.col_headings, start_col, end_col + 1)

        self.num_cols = len(self.rows[0])

    def drop_column(self, col_num):
        for row in self.rows:
            row.pop(col_num)

        if self.col_headings:
            self.col_headings.pop(col_num)
        self.num_cols = len(self.rows[0])

    def reorder_columns(self, col_nums):
        for row in self.rows:
            inplace_reorder(row, col_nums)

        if self.col_headings:
            inplace_reorder(self.col_headings, col_nums)

    def _transform_column(self, col_num, func):
        for row in self.rows:
            row[col_num] = func(row[col_num])

    def date_format(self, col_num, orig_fmt, new_fmt):
        def transform_date(value):
            if value:
                dt = datetime.datetime.strptime(value, orig_fmt)
                value = dt.strftime(new_fmt)
            return value

        self._transform_column(col_num, transform_date)

    def titleize(self, col_num):
        self._transform_column(col_num, apostrophe_safe_title)

    def substitute_string(self, col_num, orig_str, new_str):
        self._transform_column(
            col_num, lambda x: new_str if x == orig_str else x)

    def drop_headings(self):
        self.col_headings = None


class CSVCmd(cmd.Cmd):
    csv = CSV()

    istty = True
    prompt = "> "
    history = []
    environ = {}

    def oops(self, msg):
        print 'Error: %s' % msg

    def say(self, msg):
        if self.istty:
            print msg

    def precmd(self, line):
        for key, value in self.environ.iteritems():
            line = line.replace("$%s" % key, value)
        return line

    def postcmd(self, stop, line):
        self.history.append(line)
        return stop

    def do_history(self, line):
        """history [filename] - write out history

Writes to stdout if filename isn't specified.
"""
        if line:
            filename = line

            with open(filename, 'w') as f:
                f.write('\n'.join(self.history) + '\n')

            self.say("Wrote history to %s" % filename)
        else:
            for line in self.history:
                print line

    def do_read(self, line):
        """read <filename> - reads in a CSV file"""
        filename = line
        self.csv.read(filename)
        self.csv.pad_columns()
        self.say("Loaded %s" % filename)

    def do_write(self, line):
        """write [filename] - writes out CSV file

Writes to stdout if filename isn't specified.
        """
        filename = line
        self.csv.write(filename)
        if filename:
            self.say("Wrote %s" % filename)

    def do_pp(self, line):
        """pp - pretty-print data"""
        if self.csv.rows:
            self.csv.pretty_print()
        else:
            self.oops("No CSV file loaded")

    def do_setheading(self, line):
        """setheading - interpret first line of data as column headings"""
        self.csv.set_headings()

    def do_slice(self, line):
        """slice <start col> <end col> - keep only columns between start and \
end inclusive.
        """
        start_col, end_col = map(int,  line.split())
        self.csv.slice_columns(start_col, end_col)

    def do_drop(self, line):
        """drop [cols] - a list of columns to drop"""
        col_nums = map(int, line.split())
        # NOTE: need to drop columns in reverse order so the indexes don't
        # change out from under us
        for col_num in sorted(col_nums, reverse=True):
            self.csv.drop_column(col_num)

    def do_reorder(self, line):
        """reorder <col order> - reorders the column according to specified \
pattern
        """

        col_nums = map(int, line.split())
        self.csv.reorder_columns(col_nums)

    def do_dateformat(self, line):
        """dateformat <orig fmt> <new fmt> [cols] - reformat the cols from \
the original date format to the new date format
        """
        args = shlex.split(line)
        orig_fmt = args.pop(0)
        new_fmt = args.pop(0)
        col_nums = map(int, args)

        for col_num in col_nums:
            self.csv.date_format(col_num, orig_fmt, new_fmt)

    def do_titleize(self, line):
        """titleize [cols] - title-capitalize a set of columns"""
        col_nums = map(int, line.split())
        for col_num in col_nums:
            self.csv.titleize(col_num)

    def do_substr(self, line):
        """substr <orig str> <new str> [cols] - replace original string with \
new string across a set of columns
        """
        args = shlex.split(line)
        orig_str = args.pop(0)
        new_str = args.pop(0)
        col_nums = map(int, args)

        for col_num in col_nums:
            self.csv.substitute_string(col_num, orig_str, new_str)

    def do_dropheading(self, line):
        """dropheading - don't display the heading"""
        self.csv.drop_headings()

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]

        # Load up any specified environment variables
        # TODO: use acutal ENVIRON too?
        environ = {}
        for token in sys.argv[2:]:
            key, value = token.split('=')
            environ[key] = value

        with open(filename, 'rt') as f:
            csv_cmd = CSVCmd(stdin=f)
            csv_cmd.use_rawinput = False
            csv_cmd.prompt = ''
            csv_cmd.istty = False
            csv_cmd.environ = environ
            csv_cmd.cmdloop()
    else:
        CSVCmd().cmdloop()
