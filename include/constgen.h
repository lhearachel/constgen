#ifndef CONSTGEN_H
#define CONSTGEN_H

#include <filesystem>

namespace fs = std::filesystem;

namespace constgen {

enum Language {
    LANGUAGE_C,
    LANGUAGE_ASM,
    LANGUAGE_PY,
};

void generate(fs::path &schema_fname, enum Language lang);

}; // constgen

#endif // CONSTGEN_H
