from collections import namedtuple
from collections.abc import MutableSequence
from enum import auto, Enum
from pathlib import Path
from re import sub as re_sub
from typing import Optional

from schema import Definition, ConstType, CompositionOp


GENERATED_BANNER = 'THIS FILE WAS GENERATED WITH CONSTGEN; DO NOT MANUALLY MODIFY IT'
ORIGIN_FILE_BANNER = 'CONSTANTS ORIGIN FILE: {origin_file_name}'


class Language(Enum):
    C       = 0
    ASM     = auto()
    PY      = auto()


LANG_COMPOSE_OPS = [
    ['', '|'],
    ['', ''],
    ['', '|'],
]


def _file_guard(target: Path) -> str:
    return '_'.join(
        re_sub('([A-Z][a-z]+)', r' \1',
               re_sub('([A-Z]+)', r' \1',
                      str(target).replace('-', ' ')
               )
        ).split()
    ).upper().replace('/', '__').replace('.', '__')


def _compose(components: list[str], op: str, lang: Language) -> str:
    match CompositionOp[op.upper()]:
        case CompositionOp.OR:
            return LANG_COMPOSE_OPS[lang.value][CompositionOp.OR.value].join(components)

        case _:
            raise ValueError


def _generate_enum(defn: Definition,
                   f_str: str,
                   prefix_line: Optional[str] = None,
                   suffix_line: Optional[str] = None) -> MutableSequence[str]:
    start = 0
    offset = 0
    vals = []

    if prefix_line:
        vals.append(prefix_line)

    for v in defn.values:
        if v in defn.overrides:
            start = defn.overrides[v]
            offset = 0

        vals.append(f_str.format(v = v, i = start + offset))
        offset = offset + 1

    if suffix_line:
        vals.append(suffix_line)

    return '\n'.join([*vals, ''])


def c_header(target: Path, origin_file_name: Path) -> str:
    incl_guard = _file_guard(target) + '_H'
    return '\n'.join([
        f'// {GENERATED_BANNER}',
        f'// {ORIGIN_FILE_BANNER.format(origin_file_name=origin_file_name)}',
        '',
        f'#ifndef {incl_guard}',
        f'#define {incl_guard}',
        ''
    ])


def c_footer(target: Path) -> str:
    return '#endif'


def c_content(defn: Definition) -> str:
    match defn.type:
        case ConstType.ENUM:
            # C enums support a preprocessor definition style
            if defn.as_preproc:
                f_str = '#define {v} {i}'
                prefix_line = None
                suffix_line = None
            else:
                f_str = '    {v} = {i},'
                prefix_line = f'enum {defn.key[1:]} {{'
                suffix_line = '};'

            return _generate_enum(defn, f_str, prefix_line, suffix_line)

        case ConstType.FLAGS:
            vals = [f'#define {v} (1 << {i})' for i, v in enumerate(defn.values[1:])]
            composites = [f'#define {k} ({_compose(v["components"], v["op"], Language.C)})' for k, v in defn.composites.items()]

            return '\n'.join([
                f'#define {defn.values[0]} 0',
                *vals,
                *composites,
                ''
            ])

        case ConstType.ALIASES:
            # Dump literal definitions
            # Aliases can be dumped either as preprocessor defines or as enum members
            if defn.as_preproc:
                vals = [f'#define {k} {v}' for k, v in defn.values.items()]
                return '\n'.join([
                    *vals,
                    ''
                ])
            else:
                vals = [f'    {k} = {v},' for k, v in defn.values.items()]
                return '\n'.join([
                    f'enum {defn.key[1:]} {{',
                    *vals,
                    '};\n'
                ])

        case _:
            raise ValueError


def asm_header(target: Path, origin_file_name: Path) -> str:
    incl_guard = _file_guard(target) + '_INC'
    return '\n'.join([
        f'; {GENERATED_BANNER}',
        f'; {ORIGIN_FILE_BANNER.format(origin_file_name=origin_file_name)}',
        '',
        f'    .ifndef {incl_guard}',
        f'    .set {incl_guard}, 1',
        ''
    ])


def asm_footer(target: Path) -> str:
    return '    .endif'


def asm_content(defn: Definition) -> str:
    match defn.type:
        case ConstType.ENUM:
            f_str = '    .equ {v}, {i}'
            return _generate_enum(defn, f_str)

        case ConstType.FLAGS:
            # The first flag value is always interpreted as 0
            vals = [f'    .equ {v}, (1 << {i})' for i, v in enumerate(defn.values[1:])]
            composites = [f'    .equ {k}, ({_compose(v["components"], v["op"], Language.C)})' for k, v in defn.composites.items()]

            return '\n'.join([
                f'    .equ {defn.values[0]}, 0',
                *vals,
                *composites,
                ''
            ])

        case ConstType.ALIASES:
            vals = [f'    .equ {k}, {v}' for k, v in defn.values.items()]
            return '\n'.join([
                *vals,
                ''
            ])

        case _:
            raise ValueError


def py_header(target: Path, origin_file_name: Path) -> str:
    return '\n'.join([
        f'# {GENERATED_BANNER}',
        f'# {ORIGIN_FILE_BANNER.format(origin_file_name=origin_file_name)}',
        '',
        'import enum',
        ''
    ])


def py_footer(target: Path) -> str:
    return ''


def py_content(defn: Definition) -> str:
    match defn.type:
        case ConstType.ENUM:
            f_str = '    {v} = {i}'
            prefix_line = f'class {defn.key[1:]}(enum.Enum):'
            return _generate_enum(defn, f_str, prefix_line)

        case ConstType.FLAGS:
            vals = [f'    {v} = enum.auto()' for v in defn.values[1:]]
            composites = [f'    {k} = {_compose(v["components"], v["op"], Language.PY)}' for k, v in defn.composites.items()]
            return '\n'.join([
                f'class {defn.key[1:]}(enum.IntFlag):',
                f'    {defn.values[0]} = 0',
                *vals,
                *composites,
                ''
            ])

        case ConstType.ALIASES:
            vals = [f'    {k} = {v}' for k, v in defn.values.items()]
            return '\n'.join([
                f'class {defn.key[1:]}(enum.Enum):',
                *vals,
                ''
            ])

        case _:
            raise ValueError


FuncSet = namedtuple('FuncSet', ['header', 'footer', 'content'])

LANG_FUNCS = [
    FuncSet(c_header,       c_footer,       c_content),
    FuncSet(asm_header,     asm_footer,     asm_content),
    FuncSet(py_header,      py_footer,      py_content),
]

LANG_EXTS = [
    '.h',
    '.inc',
    '.py',
]
