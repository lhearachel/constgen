from collections import namedtuple
from collections.abc import MutableMapping
from enum import auto, IntFlag
from json import load as json_load, loads as json_loads
from pathlib import Path


_DEFINITIONS = 'definitions'
_TARGETS = 'targets'


Definition = namedtuple('Definition', ['key', 'type', 'values', 'composites', 'as_preproc'])
Target = namedtuple('Target', ['path', 'def_keys'])


class ConstType(IntFlag):
    NONE    = 0
    ENUM    = auto()
    FLAGS   = auto()


class CompositionOp(IntFlag):
    NONE    = 0
    OR      = auto()


def _flatten(d: MutableMapping, parent='', sep='/'):
    items = []
    for k, v in d.items():
        child = parent + sep + k if parent else k
        if isinstance(v, MutableMapping):
            items.extend(_flatten(v, child, sep).items())
        else:
            items.append((child, v))

    return dict(items)


class Schema():
    __slots__ = (_DEFINITIONS, _TARGETS)

    def __init__(self, defs: MutableMapping, targets: MutableMapping):
        self.definitions = { 
            def_key: Definition(def_key,
                                ConstType[def_obj['type'].upper()],
                                def_obj['values'],
                                def_obj.get('composites', []),
                                def_obj.get('as_preproc', False))
            for def_key, def_obj in defs.items()
        }
        self.targets = { path_key: Target(path_key, def_keys) for path_key, def_keys in _flatten(targets).items() }

    @classmethod
    def from_mapping(cls, schema_dict: MutableMapping) -> 'Schema':
        return cls(schema_dict[_DEFINITIONS], schema_dict[_TARGETS])

    @classmethod
    def from_string(cls, json_s: str) -> 'Schema':
        return cls.from_mapping(json_loads(json_s))
    
    @classmethod
    def from_file(cls, path: Path) -> 'Schema':
        with open(path, 'r', encoding='utf-8') as json_f:
            return cls.from_mapping(json_load(json_f))
