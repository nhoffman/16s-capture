#!/usr/bin/env python

"""Count reads in fast{a,q}[.gz] files

"""

import sys
import argparse
import tempfile
import subprocess
from multiprocessing import Pool
import csv


def get_count(pth):
    cmd = []
    if pth.endswith('.gz'):
        cmd.append('zgrep')
    else:
        cmd.append('grep')

    cmd.extend(['-c', '-E'])

    if 'fasta' in pth:
        cmd.append('^>')
    elif 'fastq' in pth:
        cmd.append('^@M')

    cmd.append(pth)

    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    count = result.stdout.strip()
    print(pth, count)
    return (pth, count)


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('infiles', nargs='+')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-j', '--jobs', default=1, type=int)

    args = parser.parse_args(arguments)

    with Pool(processes=args.jobs) as pool:
        counts = pool.imap_unordered(get_count, args.infiles)
        writer = csv.writer(args.outfile)
        writer.writerows(sorted(counts))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
