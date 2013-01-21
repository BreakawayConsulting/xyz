import xyz
import shutil

class Qemu(xyz.BuildProtocol):
    pkg_name = 'QEMU'
    deps = ['pkg-config', 'gettext', 'glib']

    def configure(self):
        env = {}
        ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        args = ('{source_dir_from_build}/configure',
                '--prefix={prefix}',
                '--disable-cocoa',
                '--target-list=arm-softmmu',
                '--disable-curses',
                '--disable-vnc',
                '--disable-console',
                '--enable-werror',
                '--disable-slirp',
                '--disable-curl',
                '--disable-guest-base',
                '--disable-guest-agent' ,
                '--disable-blobs',
                '--audio-drv-list=',
                '--audio-card-list=',
                '--disable-usb',
                '--disable-smartcard',
                '--disable-ide',
                #                '--exec-prefix={eprefix}',
                #                '--host={host}',
                #                '--build={build}',
                #'--target-list={target}'
                )
        base_env = {
            'LDFLAGS': ldflags,
            'PKG_CONFIG_PATH': '{devtree_dir_abs}/{host}/lib/pkgconfig'.format(**self.config),
            'QEMU_PKG_CONFIG_FLAGS': '--define-variable prefix={devtree_dir_abs} --define-variable exec_prefix={devtree_dir_abs}/{host}'.format(**self.config)
                    }
        base_env.update(env)
        self.builder.cmd(*args, env=base_env, config=self.config)

    def install(self):
        super().install()
        # Now we go and remove all the stuff we don't want.
        # In fact, it may be easy to just install manually what we do want, but
        # to try and keep this working for future version we take this
        # approach for now.

        keymaps_dir = self.builder.j('{install_dir}', self.config['prefix'][1:], 'share', 'qemu',
                                     config=self.config)
        xyz.rmtree(keymaps_dir)

        etc_dir = self.builder.j('{install_dir}', self.config['prefix'][1:], 'etc', config=self.config)
        xyz.rmtree(etc_dir)

        # Copy qemu-system-arm to the right bin location...
        bin_dir = self.builder.j('{install_dir}', self.config['prefix'][1:], 'bin', config=self.config)
        ebin_dir = self.builder.j('{install_dir}', self.config['prefix'][1:], '{host}', 'bin', config=self.config)
        xyz.ensure_dir(ebin_dir)
        shutil.copy(self.builder.j(bin_dir, 'qemu-system-arm'), ebin_dir)
        xyz.rmtree(bin_dir)

rules = Qemu
