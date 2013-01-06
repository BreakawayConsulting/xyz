import xyz
import os
import shutil

class Binutils(xyz.BuildProtocol):
    pkg_name = 'binutils'
    supported_targets = ['arm-none-eabi']

    def check(self, builder):
        if builder.target not in self.supported_targets:
            raise xyz.UsageError("Invalid target ({}) for {}".format(builder.target, self.pkg_name))

    def configure(self, builder, config):
        builder.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib',
                                 config=config)

    def install(self, builder, config):
        super().install(builder, config)
        # For some reason binutils plonks libiberty.a in the output directory
        libdir = builder.j('{install_dir_abs}', config['eprefix'][1:], 'lib', config=config)
        if os.path.exists(libdir):
            shutil.rmtree(libdir)


rules = Binutils()
