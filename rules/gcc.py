import xyz
import os
import shutil

class Gcc(xyz.BuildProtocol):
    crosstool = True
    pkg_name = 'gcc'
    supported_targets = ['arm-none-eabi']
    deps = ['texinfo', 'binutils', 'gmp', 'mpfr', 'mpc']

    def check(self, builder):
        if builder.target not in self.supported_targets:
            raise xyz.UsageError("Invalid target ({}) for {}".format(builder.target, self.pkg_name))

    def configure(self, builder, config):
        builder.cross_configure('--disable-lto',
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
                                '--with-mpfr-include={devtree_dir_abs}/include', config=config)

    def install(self, builder, config):
        super().install(builder, config)
        # For some reason gcc plonks libiberty.a in the output directory
        libdir = builder.j('{install_dir_abs}', config['eprefix'][1:], 'lib', config=config)
        if os.path.exists(libdir):
            shutil.rmtree(libdir)
        # For now we strip the man pages.
        # man pages created on different systems are (for no good reason) different!
        man_dir = builder.j('{install_dir}', config['prefix'][1:], 'share', 'man', config=config)
        shutil.rmtree(man_dir)

rules = Gcc()
