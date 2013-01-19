import xyz

class ArmToolchain(xyz.Package):
    group_only = True
    pkg_name = 'arm-toolchain'
    full_deps = [('gcc', {'target': 'arm-none-eabi'}),
                 ('binutils', {'target': 'arm-none-eabi'}),
                 ('gdb', {'target': 'arm-none-eabi'}),
                 ('stlink', {})
                 ]

rules = ArmToolchain
