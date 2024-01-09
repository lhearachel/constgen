from pathlib import Path

from lang import Language, LANG_EXTS, LANG_FUNCS
from schema import Schema


def dump(origin_file: Path, langs: list[Language], root: Path=Path('.')):
    '''Dump a schema definition to a series of files for each input language.

    Generated files will be prefixed underneath a specified root directory, if any.
    '''
    schema = Schema.from_file(origin_file)
    for path, target in schema.targets.items():
        root_and_path = root / path
        root_and_path.parent.mkdir(parents=True, exist_ok=True)

        for lang in langs:
            funcs = LANG_FUNCS[lang.value]
            ext = LANG_EXTS[lang.value]
            full_path = root_and_path.with_suffix(ext)

            with open(full_path, 'w', encoding='utf-8') as out_file:
                print(funcs.header(root_and_path, origin_file), file=out_file)
                for defn_key in target.def_keys:
                    print(funcs.content(schema.definitions[defn_key]), file=out_file)
                print(funcs.footer(root_and_path), file=out_file)
