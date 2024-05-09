#include <fstream>
#include <ios>
#include <iostream>
#include <unordered_map>

#include <nlohmann/json.hpp>

#include "constgen.h"

namespace cg = constgen;
using json = nlohmann::json;

namespace constgen {

static std::unordered_map<std::string, Operator> const OPERATOR_MAP = {
    { "or", OR },
};

static std::unordered_map<std::string, ConstantType> const TYPE_MAP = {
    { "enum",    TYPE_ENUM    },
    { "bitflag", TYPE_BITFLAG },
    { "alias",   TYPE_ALIAS   },
};

void from_json(const json &schema, EnumSchema &enum_schema)
{
    try {
        schema.at("as_preproc").get_to(enum_schema.as_preproc);
    } catch (json::exception &err) {
        // assume false if not specified
        enum_schema.as_preproc = false;
    }

    schema.at("values").get_to(enum_schema.values);

    try {
        schema.at("overrides").get_to(enum_schema.overrides);
    } catch (json::exception &err) {
        // swallow; default to empty map
    }

#ifdef CONSTGEN_DEBUG
    std::cout << std::boolalpha;
    std::cout << "as_preproc: " << enum_schema.as_preproc << std::endl;
    std::cout << std::boolalpha;

    std::cout << "values: [ ";
    for (auto &value : enum_schema.values) {
        std::cout << value << ", ";
    }
    std::cout << "]" << std::endl;

    std::cout << "overrides: [ ";
    for (auto &entry : enum_schema.overrides) {
        std::cout << entry.first << " -> " << entry.second << ", ";
    }
    std::cout << "]" << std::endl;
#endif
}

void from_json(const json &schema, BitflagComposite &composite)
{
    auto op_it = OPERATOR_MAP.find(schema.at("op")); // let the exception bubble up
    if (op_it != OPERATOR_MAP.end()) {
        composite.op = op_it->second;
    }

    schema.at("components").get_to(composite.components);
}

void from_json(const json &schema, BitflagSchema &bitflag_schema)
{
    schema.at("values").get_to(bitflag_schema.values);

    try {
        schema.at("composites").get_to(bitflag_schema.composites);
    } catch (json::exception &err) {
        // swallow; default to empty struct
    }

#ifdef CONSTGEN_DEBUG
    std::cout << "values: [ ";
    for (auto &value : bitflag_schema.values) {
        std::cout << value << ", ";
    }
    std::cout << "]" << std::endl;

    std::cout << "composites: [" << std::endl;
    for (auto &entry : bitflag_schema.composites) {
        std::cout << "  " << entry.first << " -> {" << std::endl;
        std::cout << "    op: " << entry.second.op << std::endl;
        std::cout << "    components: [ ";
        for (auto &component : entry.second.components) {
            std::cout << component << ", ";
        }
        std::cout << "]" << std::endl;
        std::cout << "  }" << std::endl;
    }
    std::cout << "]" << std::endl;
#endif
}

void from_json(const json &schema, AliasSchema &alias_schema)
{
    try {
        schema.at("as_preproc").get_to(alias_schema.as_preproc);
    } catch (json::exception &err) {
        // assume false if not specified
        alias_schema.as_preproc = false;
    }

    schema.at("values").get_to(alias_schema.values);

#ifdef CONSTGEN_DEBUG
    std::cout << std::boolalpha;
    std::cout << "as_preproc: " << alias_schema.as_preproc << std::endl;
    std::cout << std::boolalpha;

    std::cout << "values: {" << std::endl;
    for (auto &entry: alias_schema.values) {
        std::cout << "  " << entry.first << " -> " << entry.second << std::endl;
    }
    std::cout << "}" << std::endl;
#endif
}

void from_json(const json &data, Schema &schema)
{
    auto type_it = TYPE_MAP.find(data.at("type")); // let the exception bubble up
    if (type_it != TYPE_MAP.end()) {
        schema.type = type_it->second;
    }

#ifdef CONSTGEN_DEBUG
    std::cout << "type: " << schema.type << std::endl;
#endif

    switch (schema.type) {
    case TYPE_ENUM:
        schema.enum_schema = data;
        break;

    case TYPE_BITFLAG:
        schema.bitflag_schema = data;
        break;

    case TYPE_ALIAS:
        schema.alias_schema = data;
        break;
    }
}

}; // constgen

cg::Schema cg::from_json(const fs::path &schema_fname)
{
    std::ifstream ifs(schema_fname);
    if (!ifs.good()) {
        std::cerr << "Invalid input file: " << schema_fname << std::endl;
        return {};
    }

    return json::parse(ifs);
}

