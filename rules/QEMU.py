import xyz

class Qemu(xyz.BuildProtocol):
    pkg_name = 'QEMU'
    deps = ['pkg-config', 'gettext', 'glib']

    def configure(self, builder, config):
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
            'PKG_CONFIG_PATH': '{devtree_dir_abs}/{host}/lib/pkgconfig'.format(**config),
            'QEMU_PKG_CONFIG_FLAGS': '--define-variable prefix={devtree_dir_abs} --define-variable exec_prefix={devtree_dir_abs}/{host}'.format(**config)
                    }
        base_env.update(env)
        builder.cmd(*args, env=base_env, config=config)



rules = Qemu()
