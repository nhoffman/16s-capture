#!/usr/bin/env python

"""Calculate consensus for aligned, unpaired reads.

"""

import sys
import argparse
import tempfile
import subprocess
import re
from itertools import groupby
from operator import attrgetter

from fastalite import fastalite, Opener


def reformat(seq):
    return '>{}\n{}\n'.format(seq.id, seq.seq.replace('.', '-').upper())


def consensus(seq1, seq2, allow_overlap=False):
    assert len(seq1.seq) == len(seq2.seq)
    for c1, c2 in zip(seq1.seq, seq2.seq):
        if c1 == c2:
            yield c1
        elif c1 == '-':
            yield c2
        elif c2 == '-':
            yield c1
        else:
            if allow_overlap:
                yield 'N'
            else:
                raise ValueError('c1 is {} and c2 is {}'.format(c1, c2))


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('infile', type=Opener('r'))
    parser.add_argument('-o', '--outfile', default=sys.stdout,
                        type=Opener('w'))
    parser.add_argument('--allow-overlap', action='store_true', default=False)
    args = parser.parse_args(arguments)

    seqs = sorted(fastalite(args.infile), key=attrgetter('id'))
    rexp = re.compile(r'_r[12]$')

    for name, reads in groupby(seqs, key=lambda seq: rexp.sub('', seq.id)):
        reads = list(reads)
        if len(reads) == 2:
            try:
                merged = ''.join(consensus(*reads, allow_overlap=args.allow_overlap))
            except ValueError:
                continue
            else:
                args.outfile.write('>{}\n{}\n'.format(name, merged))
        else:
            args.outfile.write('>{}\n{}\n'.format(name, reads[0].seq))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
