import xyz

class PkgConfig(xyz.Package):
    pkg_name = 'pkg-config'
    deps = ['gettext', 'glib']
    uses_osx_frameworks = True

    def configure(self):
        if self.is_darwin():
            env = {'GLIB_CFLAGS': '-I{devtree_dir_abs}/include/glib-2.0 -I{devtree_dir_abs}/{host}/lib/glib-2.0/include/',
                   'GLIB_LIBS': '-L{devtree_dir_abs}/{host}/lib -lglib-2.0 -lintl -liconv -framework Carbon'}
        elif self.is_linux():
            env = {'GLIB_CFLAGS': '-I{devtree_dir_abs}/include/glib-2.0 -I{devtree_dir_abs}/{host}/lib/glib-2.0/include/',
                   'GLIB_LIBS': '-L{devtree_dir_abs}/{host}/lib -lglib-2.0 -lrt'}

        self.host_lib_configure('--disable-nls', env=env)

rules = PkgConfig
