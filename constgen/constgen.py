#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

from dump import dump as dump_from_file
from lang import Language

def constgen():
    ARG_P = ArgumentParser(
        prog='constgen',
        description='Multi-language constants-file generator'
    )
    ARG_P.add_argument('-f', '--file',
                       dest='files',
                       help='input manifest file(s) containing the consts schema',
                       nargs='+')
    ARG_P.add_argument('-r', '--root',
                       help='root directory in which to dump generated files',
                       default='.')
    ARG_P.add_argument('-l', '--lang',
                       dest='langs',
                       help='language target for generated files',
                       choices=[l.name.lower() for l in Language],
                       nargs='+')

    args = ARG_P.parse_args()

    target_root = Path(args.root)
    for target_file in args.files:
        dump_from_file(Path(target_file),
                       list(map(lambda l: Language[l.upper()], args.langs)),
                       target_root)


if __name__ == '__main__':
    constgen()
