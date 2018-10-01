#!/usr/bin/env python

import argparse
import sys


def main(arguments):

    parser = argparse.ArgumentParser()
    parser.add_argument('stats_file', help="file with raxml tree stats")
    args = parser.parse_args(arguments)

    is_dna = False
    sub_mat = None
    alpha = None
    freqs = []
    rates = []

    with open(args.stats_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("DataType:"):
                is_dna = 'DNA' in line
            elif line.startswith("Substitution Matrix"):
                sub_mat = line.split()[2]
                if sub_mat == "GTR" and not is_dna:
                    sub_mat = "PROTGTR"
            elif line.startswith("Base frequencies:"):
                freqs = line.split()[2:]
            elif line.startswith("alpha"):
                _, raw_alpha, raw_rates = line.split(':')
                alpha = raw_alpha.split()[0]
                rates = raw_rates.split()

    model = '{sub_mat}{{{rates}}}+FU{{{freqs}}}+G4{{{alpha}}}'.format(
        sub_mat=sub_mat,
        rates='/'.join(rates),
        freqs='/'.join(freqs),
        alpha=alpha
    )
    print(model)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
