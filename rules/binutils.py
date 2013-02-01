import xyz

class Binutils(xyz.BuildProtocol):
    pkg_name = 'binutils'
    variants = {
        'target': ['arm-none-eabi']
        }
    deps = ['texinfo']

    def configure(self):
        self.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib')

    def install(self):
        super().install()
        self.strip_libiberty()
        self.strip_silly_info()

        # For now we strip the man pages.
        # man pages created on different systems are (for no good reason) different!
        man_dir = self.j('{prefix_dir}', 'share', 'man')
        xyz.rmtree(man_dir)

rules = Binutils
