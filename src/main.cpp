#include <iostream>

#include <argparse/argparse.hpp>
#include <unordered_map>

#include "constgen.h"

namespace cg = constgen;

static std::unordered_map<std::string, enum cg::Language> const SUPPORTED_LANGS = {
    { "c",   cg::LANGUAGE_C   },
    { "asm", cg::LANGUAGE_ASM },
    { "py",  cg::LANGUAGE_PY  },
};

int main(int argc, char *argv[]) {
    argparse::ArgumentParser program("constgen", "1.0");

    program.add_argument("-l", "--lang")
        .metavar("LANG")
        .help("generate a header/module for LANG; choices: { c, asm, py }")
        .required();

    program.add_argument("-f", "--file")
        .metavar("FILE")
        .help("generate constants from spec FILE")
        .required();

    try {
        program.parse_args(argc, argv);
    } catch (const std::exception& err) {
        std::cerr << err.what() << std::endl;
        std::cerr << program;
        std::exit(1);
    }

    std::string fname_in = program.get("--file");

    enum cg::Language lang;
    std::string lang_in = program.get("--lang");
    auto lang_it = SUPPORTED_LANGS.find(lang_in);
    if (lang_it != SUPPORTED_LANGS.end()) {
        lang = lang_it->second;
    } else {
        std::cerr << "Unrecognized value for LANG: " << lang_in << std::endl;
        std::cerr << program;
        std::exit(1);
    }

    std::cout << "fname_in: " << fname_in << std::endl;
    std::cout << "lang:     " << lang << std::endl;

    return 0;
}

