from collections import namedtuple
from enum import auto, Enum
from pathlib import Path
from re import sub as re_sub

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
            # Enums do not support composite values
            # C enums support a preprocessor definition style
            if defn.as_preproc:
                vals = [f'#define {v} {i}' for i, v in enumerate(defn.values)]
                return '\n'.join([
                    *vals,
                    ''
                ])
            else:
                vals = [f'    {v} = {i},' for i, v in enumerate(defn.values)]
                return '\n'.join([
                    f'enum {defn.key[1:]} {{',
                    *vals,
                    '};\n'
                ])

        case ConstType.FLAGS:
            # The first flag value is always interpreted as 0
            vals = [f'#define {v} (1 << {i})' for i, v in enumerate(defn.values[1:])]
            composites = [f'#define {k} ({_compose(v["components"], v["op"], Language.C)})' for k, v in defn.composites.items()]

            return '\n'.join([
                f'#define {defn.values[0]} 0',
                *vals,
                *composites,
                ''
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
            vals = [f'    .equ {v}, {i}' for i, v in enumerate(defn.values)]
            return '\n'.join([*vals, ''])

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
            vals = [f'    {v} = {i}' for i, v in enumerate(defn.values)]
            return '\n'.join([
                f'class {defn.key[1:]}(enum.Enum):',
                *vals,
                ''
            ])

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
