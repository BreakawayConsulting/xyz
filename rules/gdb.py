import xyz

class Gdb(xyz.Package):
    pkg_name = 'gdb'
    variants = {
        'target': ['arm-none-eabi']
        }
    deps = ['texinfo', 'python']
    uses_osx_frameworks = True

    def configure(self):
        self.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib')

        # After configuring we need to ice python, but we need
        # to ensure we do it using the built version of Python, not
        # this Python
        xyz.ensure_dir('gdb')
        with xyz.chdir('gdb'):
            self.cmd('{devtree_dir_abs}/{host}/bin/python3', '{root_dir_abs}/ice/ice.py', 'stdlib')

rules = Gdb
