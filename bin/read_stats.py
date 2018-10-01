#!/usr/bin/env python

"""Count reads in fast{a,q}[.gz] files

"""

import sys
import argparse
import csv
from os import path
import re
from itertools import groupby
from operator import itemgetter
import configparser


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('data_conf')
    parser.add_argument('counts', type=argparse.FileType())
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default=sys.stdout)

    args = parser.parse_args(arguments)

    data = configparser.ConfigParser(allow_no_value=True)
    data.read(args.data_conf)
    sections = list(data.items())[1:]  # exclude DEFAULT section
    rawfiles = {section.get('r1'): label for label, section in sections}

    reader = csv.reader(args.counts)

    rows = []
    for pth, count in reader:
        if pth in rawfiles:
            specimen = rawfiles[pth]
            label = 'raw'
        else:
            __, specimen, fname = pth.split('/')
            label = (re.sub(r'\.fast[aq](\.gz)?$', '', fname.lower())
                     .replace('pear.', '')
                     .replace('_r1', '')
                     .replace('r1_', '')
                     .replace('.forward', ''))

        rows.append((specimen, label, count))

    fieldnames = """
        specimen
        raw
        barcodecop
        cleaned
        deduped
        assembled
        unassembled
        discarded
        seqs-16s
        seqs-not16s
        qalign_unmerged
        qalign""".split()

    writer = csv.DictWriter(args.outfile, fieldnames=fieldnames)
    writer.writeheader()
    for specimen, grp in groupby(sorted(rows), itemgetter(0)):
        row = dict([itemgetter(1, 2)(r) for r in grp], specimen=specimen)
        writer.writerow(row)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
