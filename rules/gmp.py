import xyz
import os
import shutil

class Gmp(xyz.BuildProtocol):
    pkg_name = 'gmp'

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Gmp()
