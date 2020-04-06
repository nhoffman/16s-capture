#!/usr/bin/env python
import argparse
import matplotlib.pyplot
import seaborn
import sys


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('fastq', nargs='+')
    parser.add_argument('out')
    parser.add_argument('--title')
    args = parser.parse_args(arguments)
    lengths = []
    seq = ''
    seq_line = False
    for f in args.fastq:
        for line in open(f):
            line = line.strip()
            if line.startswith('+'):
                seq_line = False
                lengths.append(len(seq))
                seq = ''
            elif line.startswith('@'):
                seq_line = True
            elif seq_line:
                seq += line
    seaborn.set(font_scale=1)
    fig, ax = matplotlib.pyplot.subplots(ncols=1, figsize=(10, 10))
    ax.set(
        title=args.title or None,
        xlabel='base pairs',
        ylabel='distribution')
    seaborn.kdeplot(lengths, shade=True, ax=ax)
    matplotlib.pyplot.suptitle('Sequence lengths', size=18)
    fig.savefig(args.out, format='pdf')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
