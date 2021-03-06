import xyz
import os

class Gcc(xyz.Package):
    pkg_name = 'gcc'
    variants = {
        'target': ['arm-none-eabi']
        }

    @property
    def deps(self):
        return ['texinfo', ('binutils', {'target': self.variant['target']}), 'gmp', 'mpfr', 'mpc']

    def configure(self):
        self.cross_configure('--disable-lto',
                             '--disable-nls',
                             '--enable-languages=c',
                             '--disable-libssp',
                             '--disable-libquadmath',
                             '--disable-libgomp',
                             '--disable-libgcj',
                             '--with-gnu-as',
                             '--with-gnu-ld',
                             '--with-gmp={devtree_dir_abs}/{host}',
                             '--with-mpfr-lib={devtree_dir_abs}/{host}/lib',
                             '--with-mpfr-include={devtree_dir_abs}/include')

    def install(self):
        super().install()

        # For now we strip the man pages.
        # man pages created on different systems are (for no good reason) different!
        self.rmtree('{prefix_dir}', 'share', 'man')

        # For now we are going to strip out the plugin functionality, until there
        # is usage demand for it (then it may be optional)
        lib_dir = self.j('{eprefix_dir}')
        for root, dirs, _ in os.walk(lib_dir):
            if 'plugin' in dirs:
                self.rmtree(root, 'plugin')

        lib_dir = self.j('{eprefix_dir}')
        for root, dirs, _ in os.walk(lib_dir):
            if 'install-tools' in dirs:
                self.rmtree(root, 'install-tools')
                dirs.remove('install-tools')

rules = Gcc
