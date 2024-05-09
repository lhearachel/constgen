project('constgen', 'cpp',
    meson_version: '>=1.2.0',
    version: '0.1.0'
)

argparse = dependency('argparse')
json = dependency('nlohmann_json')

public_includes = include_directories('include')

subdir('src')

constgen_exe = executable('constgen',
    sources: constgen_cpp_srcs,
    cpp_args: [
        '-std=c++20',
        '-Wall',
        '-Wpedantic',
        '-Werror',
        '-DCONSTGEN_DEBUG',
    ],
    include_directories: public_includes,
    dependencies: [
        argparse,
        json,
    ],
)

constgen_dep = declare_dependency()

meson.override_dependency('constgen', constgen_dep)
meson.override_find_program('constgen', constgen_exe)
