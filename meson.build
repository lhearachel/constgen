project('constgen',
    meson_version: '>=1.2.0',
    version: '0.1.0'
)

subdir('constgen')

############################################################
###                    FOR CONSUMERS                     ###
############################################################

constgen_dep = declare_dependency()

meson.override_dependency('constgen', constgen_dep)
meson.override_find_program('constgen_py', constgen_py)
