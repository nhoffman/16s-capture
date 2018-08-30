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
    parser.add_argument('--infile', help="Input file", default='data/data.conf')
    args = parser.parse_args(arguments)

    data = configparser.ConfigParser(allow_no_value=True)
    data.read(args.infile)
    sections = list(data.items())
    for name, sec in sections[1:]:
        for key in ['r1', 'r2']:
            pth = sec.get(key)
            assert pth is not None
            assert os.path.exists(pth)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

