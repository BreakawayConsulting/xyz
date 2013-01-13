import xyz
import os
import shutil

class Gcc(xyz.BuildProtocol):
    crosstool = True
    pkg_name = 'gcc'
    supported_targets = ['arm-none-eabi']

    def get_deps(self, config):
        return ['texinfo', ('binutils', {'target': config['target']}), 'gmp', 'mpfr', 'mpc']

    def check(self, config):
        if config['target'] not in self.supported_targets:
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
        libdir = builder.j('{install_dir_abs}', config['eprefix'][1:], 'lib', 'x86_64', config=config)
        if os.path.exists(libdir):
            shutil.rmtree(libdir)
        # For now we strip the man pages.
        # man pages created on different systems are (for no good reason) different!
        man_dir = builder.j('{install_dir}', config['prefix'][1:], 'share', 'man', config=config)
        shutil.rmtree(man_dir)

        # For now we are going to strip out the plugin functionality, until there
        # is usage demand for it (then it may be optional)
        lib_dir = builder.j('{install_dir}', config['eprefix'][1:], config=config)
        for root, dirs, _ in os.walk(lib_dir):
            if 'plugin' in dirs:
                shutil.rmtree(os.path.join(root, 'plugin'))

        lib_dir = builder.j('{install_dir}', config['eprefix'][1:], config=config)
        for root, dirs, _ in os.walk(lib_dir):
            if 'install-tools' in dirs:
                shutil.rmtree(os.path.join(root, 'install-tools'))
                dirs.remove('install-tools')

rules = Gcc()
