#!/usr/bin/env python3

"""Reformat per_query.tsv (output of 'gappa assign')

see https://github.com/lczech/gappa/wiki/Subcommand:-assign

Use "afract" for filtering, based on two criteria.

1. keep lineages with afract => min-afract
2. keep ranks with a cumulative value of afract >= min-total

Consider the following classification:

name    LWR     fract   aLWR    afract  taxopath
seqname 0       0       0.9998  1       k__Bacteria
seqname 0       0       0.9998  1       k__Bacteria;p__Bacteroidetes
seqname 0       0       0.9998  1       k__Bacteria;p__Bacteroidetes;c__Bacteroidia
seqname 0       0       0.9998  1       k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales
seqname 0       0       0.9998  1       k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Bacteroidaceae
seqname 0.8704  0.8706  0.9998  1       k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Bacteroidaceae;g__Bacteroides
seqname 2.37e-05        2.371e-05       2.37e-05        2.371e-05       k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Bacteroidaceae;g__Bacteroides;s__Bacteroides_vulgatus
seqname 0.1293  0.1293  0.1293  0.1293  k__Bacteria;p__Bacteroidetes;c__Bacteroidia;o__Bacteroidales;f__Bacteroidaceae;g__Bacteroides;s__Bacteroides_mediterraneensis
"""

import os
import sys
import argparse
import csv
from collections import OrderedDict, Counter
from itertools import groupby
from operator import itemgetter

RANKS = OrderedDict(
    [('k', 'kingdom'),
     ('p', 'phylum'),
     ('c', 'class'),
     ('o', 'order'),
     ('f', 'family'),
     ('g', 'genus'),
     ('s', 'species')]
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


def parse_row(row):
    d = dict(row)
    d['seqname'] = d.pop('name')
    for key in ['LWR', 'fract', 'aLWR', 'afract']:
        d[key] = float(d[key])

    classification = d.pop('taxopath').split(';')[-1]
    rank, d['name'] = classification.split('__')
    d['rank'] = RANKS[rank]

    return d


def filter_lineages(lines, min_afract, min_total):
    for rank, grp in groupby(lines, itemgetter('rank')):
        grp = [line for line in grp if line['afract'] >= min_afract]
        likelihood = sum(line['afract'] for line in grp)
        if likelihood >= min_total:
            yield {
                'rank': rank,
                'tax_name': concat_names([line['name'] for line in grp], rank=rank),
                'likelihood': likelihood,
            }


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('-c', '--classifications',
                        help="most specific classification for each sequence",
                        default=sys.stdout, type=argparse.FileType('w'))
    parser.add_argument('-l', '--lineages',
                        help="full lineage for each sequence",
                        type=argparse.FileType('w'))
    parser.add_argument('-k', '--krona',
                        help="tabular output for krona plot using 'ktImportText'",
                        type=argparse.FileType('w'))
    parser.add_argument('--min-afract', type=float, default=0.05,
                        help='minimum value for afract for each lineage [%(default)s]')
    parser.add_argument('--min-total', type=float, default=0.1,
                        help=('minimum sum of values of afract '
                              'for all lineages in a rank [%(default)s]'))

    args = parser.parse_args(arguments)
    rank_orders = {rank: i for i, rank in enumerate(RANKS.values(), 1)}

    reader = csv.DictReader(args.infile, delimiter='\t')
    queries = groupby(map(parse_row, reader), itemgetter('seqname'))

    if args.classifications:
        classif = csv.DictWriter(
            args.classifications, fieldnames=['name', 'rank', 'tax_name', 'likelihood'],
            extrasaction='ignore')
        classif.writeheader()

    if args.lineages:
        fieldnames = ['name', 'rank', 'tax_name', 'likelihood'] + list(RANKS.values())
        lineages = csv.DictWriter(args.lineages, fieldnames=fieldnames)
        lineages.writeheader()

    if args.krona:
        fieldnames = ['count'] + list(RANKS.values())
        krona = csv.DictWriter(args.krona, fieldnames=fieldnames, delimiter='\t')

    counts = Counter()
    for name, lines in queries:
        lineage = list(filter_lineages(
            lines, min_afract=args.min_afract, min_total=args.min_total))

        # last row provides the most specific classification
        most_specific = dict(name=name, **lineage[-1])
        ranks = tuple([(L['rank'], L['tax_name']) for L in lineage])
        counts[ranks] += 1

        if args.classifications:
            classif.writerow(most_specific)

        # tabular representation of entire lineage
        if args.lineages:
            lineages.writerow(dict(most_specific, **dict(ranks)))

    if args.krona:
        for lineage, count in counts.most_common():
            krona.writerow(dict(count=count, **dict(lineage)))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

