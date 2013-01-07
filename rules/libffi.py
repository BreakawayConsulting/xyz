import xyz
import os
import shutil

class Libffi(xyz.BuildProtocol):
    pkg_name = 'libffi'

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Libffi()
