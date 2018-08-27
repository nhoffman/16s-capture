#!/usr/bin/env python

"""Merge two Stockholm-format multiple alignments produced by the same
profile using esl-alimerge, then write the two corresponding
fasta-format alignments.

"""

import sys
import argparse
import tempfile
import subprocess

from fastalite import fastalite, Opener


def reformat(seq):
    return '>{}\n{}\n'.format(seq.id, seq.seq.replace('.', '-').upper())


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    inputs = parser.add_argument_group('input files')
    inputs.add_argument('sto_1', type=Opener('r'))
    inputs.add_argument('sto_2', type=Opener('r'))

    outputs = parser.add_argument_group('output files')
    inputs.add_argument('fasta_1', type=Opener('w'))
    inputs.add_argument('fasta_2', type=Opener('w'))

    args = parser.parse_args(arguments)

    input1_names = {line.split()[0] for line in args.sto_1
                    if line.strip() and not line.startswith('#')}

    with tempfile.NamedTemporaryFile('w+t', dir='.') as tf:
        cmd = ['esl-alimerge',
               '--dna',
               '--outformat', 'afa',
               '-o', tf.name,
               args.sto_1.name, args.sto_2.name]
        sys.stderr.write(' '.join(cmd) + '\n')
        p = subprocess.Popen(cmd)
        p.communicate()

        merged = fastalite(tf)
        for seq in merged:
            if seq.id in input1_names:
                args.fasta_1.write(reformat(seq))
            else:
                args.fasta_2.write(reformat(seq))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
