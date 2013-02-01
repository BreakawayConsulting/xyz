import xyz

class Binutils(xyz.Package):
    pkg_name = 'binutils'
    variants = {
        'target': ['arm-none-eabi']
        }
    deps = ['texinfo']

    def configure(self):
        self.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib')

    def install(self):
        super().install()
        # For now we strip the man pages.
        # man pages created on different systems are (for no good reason) different!
        self.rmtree('{prefix_dir}', 'share', 'man')

rules = Binutils
