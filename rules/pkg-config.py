import xyz
import os
import shutil

class PkgConfig(xyz.BuildProtocol):
    pkg_name = 'pkg-config'
    deps = ['gettext', 'glib']

    def configure(self, builder, config):
        env = {'GLIB_CFLAGS': "-I{devtree_dir_abs}/include/glib-2.0 -I{devtree_dir_abs}/{host}/lib/glib-2.0/include/",
               'GLIB_LIBS': '-L{devtree_dir_abs}/{host}/lib -lglib-2.0 -lintl -liconv -framework Carbon',
               'LDFLAGS': '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'.format(**config)}

        #'LDFLAGS': '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'.format(**config)}
        # FIXME: doesn't understand --disable-shared (it isn't a lib, so no surprise there!)
        builder.host_lib_configure('--disable-nls', config=config, env=env)

rules = PkgConfig()
