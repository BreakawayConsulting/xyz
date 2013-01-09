import xyz
import os
import shutil

class Gmp(xyz.BuildProtocol):
    pkg_name = 'gmp'
    deps = ['texinfo']

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Gmp()
