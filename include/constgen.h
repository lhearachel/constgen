#ifndef CONSTGEN_H
#define CONSTGEN_H

#include <filesystem>
#include <map>
#include <vector>

namespace fs = std::filesystem;

namespace constgen {

enum Language {
    LANGUAGE_C,
    LANGUAGE_ASM,
    LANGUAGE_PY,
};

enum ConstantType {
    TYPE_ENUM,
    TYPE_BITFLAG,
    TYPE_ALIAS,
};

enum Operator {
    OR,
};

struct EnumSchema {
    bool as_preproc;
    std::vector<std::string> values;
    std::map<std::string, int> overrides;
};

struct BitflagComposite {
    enum Operator op;
    std::vector<std::string> components;
};

struct BitflagSchema {
    std::vector<std::string> values;
    std::map<std::string, BitflagComposite> composites;
};

struct AliasSchema {
    bool as_preproc;
    std::map<std::string, int> values;
};

struct Schema {
    ConstantType type;
    EnumSchema enum_schema;
    BitflagSchema bitflag_schema;
    AliasSchema alias_schema;
};

Schema from_json(const fs::path &schema_fname);

}; // constgen

#endif // CONSTGEN_H
