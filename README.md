# `constgen`

A simple Python package for generating multi-language constants files.

## Problem Statement

Multi-language projects sometimes must share constants definitions across source files in each of those languages. This leads to the definition of multiple sources of truth and requires the maintenance of each file whenever any changes must be made. Rather than invest the effort to write a lexer or parser to extract this information, these files can instead be generated for each language from a single definition.

## Usage

Suppose that our project requires the definition of the following constants, here expressed as Python enums:

```py
import enum

class Color(enum.Enum):
    COLOR_RED    = 0
    COLOR_ORANGE = auto()
    COLOR_YELLOW = auto()
    COLOR_GREEN  = auto()
    COLOR_BLUE   = auto()
    COLOR_INDIGO = auto()
    COLOR_VIOLET = auto()

class Pet(enum.Enum):
    PET_DOG    = 0
    PET_CAT    = auto()
    PET_FISH   = auto()
    PET_LIZARD = auto()
    PET_SNAKE  = auto()
    PET_SPIDER = auto()
```

These constants can be defined instead using the following simple JSON manifest:

```json
{
    "targets": {
        "constants": [
            "@Color",
            "@Pet"
        ]
    },
    "definitions": {
        "@Color": {
            "type": "enum",
            "values": [
                "COLOR_RED",
                "COLOR_ORANGE",
                "COLOR_YELLOW",
                "COLOR_GREEN",
                "COLOR_BLUE",
                "COLOR_INDIGO",
                "COLOR_VIOLET"
            ]
        },
        "@Pet": {
            "type": "enum",
            "values": [
                "PET_DOG",
                "PET_CAT",
                "PET_FISH",
                "PET_LIZARD",
                "PET_SNAKE",
                "PET_SPIDER"
            ]
        }
    }
}
```

This manifest can then be fed into `constgen` to generate corresponding definitions for e.g., a multi-language project needing to support both C and Assembly:

```sh
python constgen/io.py -f manifest.json -r <root_path_for_generated_files> -l c asm
```
