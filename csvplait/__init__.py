"""
csvplait - Interactive Tool for Manipulating CSV files

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

import csv as csv_module
import datetime
import functools
import re
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


