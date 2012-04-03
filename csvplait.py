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
import csv
import datetime
import re

import prettytable


class CSVPlaitCmd(cmd.Cmd):
    prompt = "> "

    def do_load(self, line):
        filename = line

        with open(filename, 'r') as f:
            self.rows = load_csv(f)

        print "Loaded %s" % filename

    def do_print(self, line):
        headings = ['%d: %s' % (idx, heading) for idx, heading in
                    enumerate(self.rows[0])]

        table = prettytable.PrettyTable(headings)

        for row in self.rows[1:]:
            row = _clip_fields(row, 25)
            table.add_row(row)

        print table

    def do_drop(self, line):
        col = int(line)
        for row in self.rows:
            row.pop(col)

    def do_slice(self, line):
        start_col, end_col = line.split()
        start_col = int(start_col)
        end_col = int(end_col)
        rows = []
        for row in self.rows:
            rows.append(row[start_col:end_col + 1])
        self.rows = rows

    def do_sub(self, line):
        col, findstr, replace = line.split()
        col = int(col)

        def replace_func(value):
            return replace if value == findstr else value

        transform_column(self.rows[1:], col, replace_func)

    def do_titleize(self, line):
        col = int(line)
        transform_column(self.rows[1:], col, apostrophe_safe_title)

    def do_write(self, line):
        filename = line

        with open(filename, 'wb') as f:
            write_csv(f, self.rows)

        print "Wrote %s" % filename

    def do_reorder(self, line):
        col_order = [int(col) for col in line.split()]
        # TODO: validate that col_order values make sense
        rows = []
        for row in self.rows:
            new_row = []
            for col in col_order:
                new_row.append(row[col])
            rows.append(new_row)
        self.rows = rows

    def do_dateformat(self, line):
        col, rest = line.split(' ', 1)
        col = int(col)
        args = [x for x in rest.split('"') if x.strip()]
        from_fmt, to_fmt = args

        def transform_date(value):
            if value:
                dt = datetime.datetime.strptime(value, from_fmt)
                value = dt.strftime(to_fmt)
            return value

        transform_column(self.rows[1:], col, transform_date)


    def do_EOF(self, line):
        return True


def _clip_fields(row, width):
    clipped_row = []
    for field in row:
        if len(field) > width:
            field = field[:width] + '...'
        clipped_row.append(field)
    return clipped_row


def load_csv(fileobj):
    max_cols = 0
    rows = []
    reader = csv.reader(fileobj)
    for row in reader:
        rows.append(row)
        if len(row) > max_cols:
            max_cols = len(row)

    # pad columns
    for row in rows:
        if max_cols > len(row):
            row.extend([""] * (max_cols - len(row)))
    return rows


def write_csv(fileobj, rows):
    writer = csv.writer(fileobj)
    writer.writerows(rows)


def transform_column(rows, col, func):
    for row in rows:
        row[col] = func(row[col])


def apostrophe_safe_title(s):
    """Like `str.title` but handles apostrophes

    see http://bugs.python.org/issue7008
    """
    return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), s.title())


if __name__ == '__main__':
    CSVPlaitCmd().cmdloop()
