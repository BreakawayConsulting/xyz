import xyz

class Glib(xyz.Package):
    pkg_name = 'glib'
    deps = ['libffi', 'gettext']
    uses_osx_frameworks = True

    def configure(self):
        env = {'LIBFFI_CFLAGS': '-I{devtree_dir_abs}/{host}/lib/libffi-3.0.11-rc2/include/',
               'LIBFFI_LIBS': '-L{devtree_dir_abs}/{host}/lib -lffi'}
        self.host_lib_configure(env=env)

rules = Glib
