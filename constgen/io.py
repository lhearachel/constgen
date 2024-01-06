from argparse import ArgumentParser
from pathlib import Path

from lang import Language, LANG_EXTS, LANG_FUNCS
from schema import Schema


def dump(schema: Schema, langs: list[Language], root: Path=Path('.')):
    '''Dump a schema definition to a series of files for each input language.

    Generated files will be prefixed underneath a specified root directory, if any.
    '''
    for path, target in schema.targets.items():
        root_and_path = root / path
        root_and_path.parent.mkdir(parents=True, exist_ok=True)

        for lang in langs:
            funcs = LANG_FUNCS[lang.value]
            ext = LANG_EXTS[lang.value]
            full_path = root_and_path.with_suffix(ext)

            with open(full_path, 'w', encoding='utf-8') as out_file:
                print(funcs.header(root_and_path), file=out_file)
                for defn_key in target.def_keys:
                    print(funcs.content(schema.definitions[defn_key]), file=out_file)
                print(funcs.footer(root_and_path), file=out_file)


def dump_from_file(mapping: Path, langs: list[Language], root: Path=Path('.')):
    '''Convenience wrapper for dumping a schema defined in a manifest file.'''
    dump(Schema.from_file(mapping), langs, root)


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
