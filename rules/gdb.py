import xyz

class Gdb(xyz.BuildProtocol):
    pkg_name = 'gdb'
    variants = {
        'target': ['arm-none-eabi']
        }
    deps = ['texinfo', 'python']

    def configure(self):
        if self.config['host'].endswith('darwin'):
            ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        else:
            ldflags = '{standard_ldflags}'

        self.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib',
                                 env={'LDFLAGS': ldflags})

        # After configuring we need to ice python, but we need
        # to ensure we do it using the built version of Python, not
        # this Python
        xyz.ensure_dir('gdb')
        with xyz.chdir('gdb'):
            self.cmd('{devtree_dir_abs}/{host}/bin/python3', '{root_dir_abs}/ice/ice.py', 'stdlib')

    def install(self):
        super().install()
        self.strip_libiberty()
        self.strip_silly_info()

rules = Gdb
