import xyz

class Glib(xyz.BuildProtocol):
    pkg_name = 'glib'
    deps = ['libffi', 'gettext']

    def configure(self):
        env = {'LIBFFI_CFLAGS': '-I{devtree_dir_abs}/{host}/lib/libffi-3.0.11-rc2/include/',
               'LIBFFI_LIBS': '-L{devtree_dir_abs}/{host}/lib -lffi',
               'LDFLAGS': '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'.format(**self.config)}
        self.host_lib_configure(env=env)

rules = Glib
