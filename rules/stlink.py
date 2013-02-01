import xyz
import shutil

class Stlink(xyz.Package):
    pkg_name = 'stlink'
    deps = ['libusb']
    def configure(self):
        pass

    def make(self):
        if self.is_darwin():
            os_ldflags = 'OS_LDFLAGS="-lobjc -Wl,-framework,IOKit -Wl,-framework,CoreFoundation"'
        else:
            os_ldflags = 'OS_LDFLAGS="-lpthread -lrt"'
        self.cmd('make', '-f', '{source_dir_from_build}/Makefile',
                         'LIBUSB_CFLAGS=-I{devtree_dir_abs}/include/libusb-1.0',
                         'LIBUSB_LDFLAGS=-L{devtree_dir_abs}/{host}/lib',
                         os_ldflags,
                         '{jobs}')

    def install(self):
        install_dir = self.j('{install_dir_abs}', '{host}', 'bin')
        with xyz.chdir(self.config['build_dir']):
            self.ensure_dir(install_dir)
            shutil.copy('st-util', install_dir)

rules = Stlink
