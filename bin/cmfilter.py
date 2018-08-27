#!/usr/bin/env python

"""Filter seqs according to an alignment profile using cmsearch

The alignment profile must be calibrated using cmcalibrate. See
documentation for cmsearch for details:
http://eddylab.org/infernal/Userguide.pdf

Retained sequences are converted to the plus orientation.
"""

from __future__ import print_function
import sys
import argparse
import tempfile
import subprocess
import shutil

from fastalite import fastalite

complements = {'A': 'T', 'C': 'G', 'B': 'V', 'D': 'H', 'G': 'C', 'H':
               'D', 'K': 'M', '-': '-', 'M': 'K', 'N': 'N', 'S': 'S', 'R': 'Y', 'U':
               'A', 'T': 'A', 'W': 'W', 'V': 'B', 'Y': 'R', '.':'.', '~':'~'}


def revcomp(instr, charmap=complements):
    return ''.join([charmap.get(char, 'X') for char in reversed(instr.upper())])


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('seqs', type=argparse.FileType('r'),
                        help="Input fasta file")
    parser.add_argument('cmfile', help="Calibrated cmfile")
    parser.add_argument('-o', '--outfile', default=sys.stdout, metavar='FILE',
                        type=argparse.FileType('w'),
                        help="Fasta of seqs passing filtering criteria")
    parser.add_argument('--discarded', type=argparse.FileType('w'), metavar='FILE',
                        help="Fasta of seqs NOT passing filtering criteria")
    parser.add_argument('--scores', metavar='FILE',
                        help="Save output of 'cmsearch --tblout' to FILE")
    parser.add_argument('-e', '--min-evalue', type=float, metavar='FLOAT',
                        default=0.01,
                        help='min E-value for significance [%(default)s]')
    parser.add_argument('--cmsearch', default='cmsearch',
                        help='path to cmsearch executable [%(default)s]')
    parser.add_argument('--cpu', type=int, default=10, metavar='N',
                        help='number of CPUs [%(default)s]')
    parser.add_argument('--reverse-complement', action='store_true', default=False,
                        help=('write reverse complement of '
                              'sequences matching the negative strand'))

    args = parser.parse_args(arguments)

    # run cmsearch
    NAME, STRAND, E_VAL = 0, 9, 15

    with tempfile.NamedTemporaryFile('w+t', dir='.') as tf:
        cmd = [args.cmsearch,
               '--noali',
               '--hmmonly',
               '--tblout', tf.name,
               '--cpu', str(args.cpu),
               args.cmfile, args.seqs.name]
        sys.stderr.write(' '.join(cmd) + '\n')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()
        lines = [line.split() for line in tf.readlines()
                 if line.strip() and not line.startswith('#')]

        keep = {line[NAME]: line[STRAND]
                for line in lines if float(line[E_VAL]) <= args.min_evalue}

        if args.scores:
            shutil.copyfile(tf.name, args.scores)

    for seq in fastalite(args.seqs):
        if seq.id in keep:
            if keep[seq.id] == '-' and args.reverse_complement:
                args.outfile.write('>{}\n{}\n'.format(seq.id, revcomp(seq.seq)))
            else:
                args.outfile.write('>{}\n{}\n'.format(seq.id, seq.seq))

        elif args.discarded:
            args.discarded.write('>{}\n{}\n'.format(seq.id, seq.seq))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
