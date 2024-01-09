from collections import namedtuple
from enum import auto, Enum
from pathlib import Path
from re import sub as re_sub

from schema import Definition


GENERATED_BANNER = 'THIS FILE WAS GENERATED WITH CONSTGEN; DO NOT MANUALLY MODIFY IT'
ORIGIN_FILE_BANNER = 'CONSTANTS ORIGIN FILE: {origin_file_name}'


def _file_guard(target: Path) -> str:
    return '_'.join(
        re_sub('([A-Z][a-z]+)', r' \1',
               re_sub('([A-Z]+)', r' \1',
                      str(target).replace('-', ' ')
               )
        ).split()
    ).upper()


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
    vals = [f'    {v} = {i},' for i, v in enumerate(defn.values)]
    return '\n'.join([
        f'enum {defn.key[1:]} {{',
        *vals,
        '};\n'
    ])


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
    vals = [f'    .equ {v} {i}' for i, v in enumerate(defn.values)]
    return '\n'.join([*vals, ''])


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
    vals = [f'    {v} = {i}' for i, v in enumerate(defn.values)]
    return '\n'.join([
        f'class {defn.key[1:]}(enum.Enum):',
        *vals,
        ''
    ])


class Language(Enum):
    C       = 0
    ASM     = auto()
    PY      = auto()


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
