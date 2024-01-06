from collections import namedtuple
from enum import auto, Enum
from pathlib import Path

from schema import Definition


def c_header(target: Path) -> str:
    incl_guard = str(target).upper().replace('/', '__').replace('.', '_') + '_H'
    return f'#ifndef {incl_guard}\n#define {incl_guard}\n'


def c_footer(target: Path) -> str:
    return '#endif'


def c_content(defn: Definition) -> str:
    vals = [f'    {defn.prefix}_{v} = {i},' for i, v in enumerate(defn.values)]
    return '\n'.join([
        f'enum {defn.key[1:]} {{',
        *vals,
        '};\n'
    ])


def asm_header(target: Path) -> str:
    incl_guard = 'ASM_' + str(target).upper().replace('/', '__').replace('.', '_') + '_INC'
    return f'    .ifndef {incl_guard}\n    .set {incl_guard}, 1\n'


def asm_footer(target: Path) -> str:
    return '    .endif'


def asm_content(defn: Definition) -> str:
    vals = [f'    .equ {defn.prefix}_{v} {i}' for i, v in enumerate(defn.values)]
    return '\n'.join([*vals, ''])


def py_header(target: Path) -> str:
    return 'import enum\n'


def py_footer(target: Path) -> str:
    return ''


def py_content(defn: Definition) -> str:
    vals = [f'    {defn.prefix}_{v} = {i}' for i, v in enumerate(defn.values)]
    return '\n'.join([
        f'class {defn.key[1:]}(enum.Enum):',
        *vals,
        '\n'
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
