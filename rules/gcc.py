import xyz
import os
import shutil

class Gcc(xyz.BuildProtocol):
    pkg_name = 'gcc'
    supported_targets = ['arm-none-eabi']
    deps = ['binutils', 'gmp', 'mpfr', 'mpc']

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


rules = Gcc()
