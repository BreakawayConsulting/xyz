import xyz
import shutil

class Qemu(xyz.Package):
    pkg_name = 'QEMU'
    deps = ['pkg-config', 'gettext', 'glib']
    uses_osx_frameworks = True

    def configure(self):
        args = ('{source_dir_from_build}/configure',
                '--prefix={prefix}',
                '--disable-cocoa',
                '--target-list=arm-softmmu',
                '--disable-curses',
                '--disable-vnc',
                '--disable-tools',
                '--without-pixman',
                '--disable-console',
                '--disable-default-devices',
                '--enable-werror',
                '--disable-slirp',
                '--disable-curl',
                '--disable-guest-base',
                '--disable-guest-agent' ,
                '--disable-blobs',
                '--audio-drv-list=',
                '--audio-card-list=',
                '--disable-usb',
                '--disable-ide',
                '--disable-pie',
                '--enable-debug',
                )
        base_env = {
            'PKG_CONFIG_PATH': '{devtree_dir_abs}/{host}/lib/pkgconfig',
            'QEMU_PKG_CONFIG_FLAGS': '--define-variable prefix={devtree_dir_abs} --define-variable exec_prefix={devtree_dir_abs}/{host} --static',
                    }
        self.cmd(*args, env=base_env)

    def install(self):
        super().install()
        # Now we go and remove all the stuff we don't want.
        # In fact, it may be easy to just install manually what we do want, but
        # to try and keep this working for future version we take this
        # approach for now.
        self.rmtree('{prefix_dir}', 'share', 'qemu')
        self.rmtree('{prefix_dir}', 'etc')

        # Copy qemu-system-arm to the right bin location...
        bin_dir = self.j('{prefix_dir}', 'bin')
        ebin_dir = self.j('{eprefix_dir}', 'bin')
        self.ensure_dir(ebin_dir)
        shutil.copy(self.j(bin_dir, 'qemu-system-arm'), ebin_dir)
        self.rmtree(bin_dir)

rules = Qemu
