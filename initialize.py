#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
import csv
from scripts.encode_emoji import replace_emoji_characters

in_file_path = sys.argv[1]
dir_path = '/'.join(in_file_path.split('/')[:-1])
file_name = in_file_path.split('/')[-1].split('.csv')[0]
out_file_name = file_name + "_0.csv"
out_file_path = os.path.join(dir_path, out_file_name)

f_in = open(in_file_path, 'r')
f_out = open(out_file_path, 'w')
csv_reader = csv.reader(f_in)
csv_writer = csv.writer(f_out)

column_length = 0
for i, row in enumerate(csv_reader):
    skip = False

    if i == 0:
        column_length = len(row)
        if column_length <= 1:
            print("Columns must have at least length of two (e.g., id, sent)")
            exit(1)
        row = row + ["alpha", "beta", "mode", "var"]
    else:
        if len(row) != column_length:
            print("skipped invalid row: {}".format(row))
            skip = True
        else:
            row_encoded = []
            for r in row:
                row_encoded.append(replace_emoji_characters(r))
            row = row_encoded + ["1", "1", "0.5", "0.0833"]

    if skip:
        pass
    else:
        csv_writer.writerow(row)

