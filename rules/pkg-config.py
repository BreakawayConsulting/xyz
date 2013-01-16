import xyz

class PkgConfig(xyz.BuildProtocol):
    pkg_name = 'pkg-config'
    deps = ['gettext', 'glib']

    def configure(self):
        if self.config['host'].endswith('darwin'):
            env = {'GLIB_CFLAGS': '-I{devtree_dir_abs}/include/glib-2.0 -I{devtree_dir_abs}/{host}/lib/glib-2.0/include/',
                   'GLIB_LIBS': '-L{devtree_dir_abs}/{host}/lib -lglib-2.0 -lintl -liconv -framework Carbon',
                   'LDFLAGS': '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'}
        else:
            env = {'GLIB_CFLAGS': '-I{devtree_dir_abs}/include/glib-2.0 -I{devtree_dir_abs}/{host}/lib/glib-2.0/include/',
                   'GLIB_LIBS': '-L{devtree_dir_abs}/{host}/lib -lglib-2.0 -lrt',
                   'LDFLAGS': '{standard_ldflags}'}

        self.host_lib_configure('--disable-nls', env=env)

rules = PkgConfig
