#!/usr/bin/env python

"""Reformat of output/per_pquery_assign (output of 'gappa assign')

see https://github.com/lczech/gappa/wiki/Subcommand:-assign

Use afract for filtering, based on two criteria.

1. keep lineages with afract => min-afract
2. keep ranks with a cumulative value of afract >= min-total

Consider the following classification:

NC_009617_Cbei_R0081
0       0       1       1       k__Bacteria
0       0       1       1       k__Bacteria;p__Firmicutes
0       0       1       1       k__Bacteria;p__Firmicutes;c__Clostridia
0       0       1       1       k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales
0       0       1       1       k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Clostridiaceae
0.5823  0.5823  1       1       k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Clostridiaceae;g__Clostridium
0.2804  0.2804  0.2804  0.2804  k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Clostridiaceae;g__Clostridium;s__Clostridium_diolis
0.1372  0.1372  0.1372  0.1372  k__Bacteria;p__Firmicutes;c__Clostridia;o__Clostridiales;f__Clostridiaceae;g__Clostridium;s__Clostridium_beijerinckii

"""

import os
import sys
import argparse
import csv
from collections import OrderedDict
from itertools import groupby
from operator import itemgetter

RANKS = OrderedDict(
    k='kingdom',
    p='phylum',
    c='class',
    o='order',
    f='family',
    g='genus',
    s='species',
)


def concat_names(taxnames, rank, sep='/', splitchar='_'):
    """Heuristics for creating a sensible combination of species names."""

    if len(taxnames) == 1:
        return ' '.join(taxnames[0].split(splitchar))

    splits = [x.split(splitchar) for x in taxnames]
    if (rank == 'species'
        and all(len(x) > 1 for x in splits)
        and len(set(s[0] for s in splits)) == 1):
        name = '%s %s' % (splits[0][0],
                          sep.join(sorted('_'.join(s[1:]) for s in splits)))
    else:
        name = sep.join(' '.join(s) for s in splits)

    return name


def parse_line(x, ranks=RANKS):
    d = {}
    for key in ['lwr', 'fract', 'alwr', 'afract']:
        d[key] = float(x.pop(0))

    classification = x[0].split(';')[-1]
    rank, name = classification.split('__')
    d['rank'] = ranks[rank]
    d['name'] = name

    return d


def get_queries(fobj):

    name, lines = None, []
    for line in fobj:
        spl = line.split()
        if len(spl) == 1:
            if name:
                yield (name, lines)
            name, lines = spl[0], []
        else:
            lines.append(parse_line(spl))

    if name and lines:
        yield (name, lines)


def filter_lineages(lines, min_afract, min_total):
    for rank, grp in groupby(lines, itemgetter('rank')):
        grp = [line for line in grp if line['afract'] >= min_afract]
        likelihood = sum(line['afract'] for line in grp)
        if likelihood >= min_total:
            tax_name = concat_names([line['name'] for line in grp], rank=rank)
            yield (rank, tax_name, likelihood)


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))
    parser.add_argument('--min-afract', type=float, default=0,
                        help='minimum value for afract for each lineage [%(default)s]')
    parser.add_argument('--min-total', type=float, default=0,
                        help='minimum sum of values of afract for all lineages in a rank [%(default)s]')

    args = parser.parse_args(arguments)
    rank_orders = {rank: i for i, rank in enumerate(RANKS.values(), 1)}

    queries = get_queries(args.infile)

    writer = csv.DictWriter(
        args.outfile, fieldnames=['name', 'want_rank', 'rank', 'rank_order', 'tax_id', 'tax_name', 'likelihood'])
    writer.writeheader()

    for name, lines in queries:
        lineages = filter_lineages(lines, min_afract=args.min_afract, min_total=args.min_total)
        for rank, tax_name, likelihood in lineages:
            row = dict(
                name=name,
                want_rank=rank,
                rank=rank,
                rank_order=rank_orders[rank],
                tax_id=None,
                tax_name=tax_name,
                likelihood=likelihood,
            )
            writer.writerow(row)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

