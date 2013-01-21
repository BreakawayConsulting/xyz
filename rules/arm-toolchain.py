import xyz

class ArmToolchain(xyz.BuildProtocol):
    group_only = True
    pkg_name = 'arm-toolchain'
    deps = [('gcc', {'target': 'arm-none-eabi'}),
            ('binutils', {'target': 'arm-none-eabi'}),
            ('gdb', {'target': 'arm-none-eabi'}),
            ('stlink', {})
            ]

rules = ArmToolchain
