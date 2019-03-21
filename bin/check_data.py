#!/usr/bin/env python

import configparser

"""check data.conf

"""

import os
import sys
import argparse


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--infile', help="Input file", default='data.conf')
    args = parser.parse_args(arguments)
    print('checking {}\n'.format(args.infile))

    data = configparser.ConfigParser(allow_no_value=True)
    data.read(args.infile)

    sections = list(data.items())
    for name, sec in sections[1:]:

        r1 = sec.get('r1')
        r2 = sec.get('r2')

        if sec.get('barcodecop') == 'no':
            index_reads = []
        elif sec.get('indexing') == 'single':
            index_reads = [r1.replace('_R1_', '_I1_')]
        elif sec.get('indexing') == 'dual':
            index_reads = [r1.replace('_R1_', '_I1_'), r1.replace('_R1_', '_I2_')]
        else:
            raise ValueError('invalid value for indexing: "{}"'.format(sec.get('indexing')))

        missing = []
        for pth in [r1, r2] + index_reads:
            assert pth is not None
            if not os.path.exists(pth):
                print('{} not found'.format(pth))
                missing.append(pth)

    if missing:
        return 1
    else:
        print('ok')




if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

