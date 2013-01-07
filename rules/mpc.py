import xyz
import os
import shutil

class Mpc(xyz.BuildProtocol):
    pkg_name = 'mpc'
    deps = ['gmp', 'mpfr']

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Mpc()
