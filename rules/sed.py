import xyz
import os
import shutil

class Sed(xyz.BuildProtocol):
    pkg_name = 'sed'

    def configure(self, builder, config):
        # FIXME: doen't understand --disable-shared (it isn't a lib, so not surprise ther!)
        builder.host_lib_configure(config=config)

rules = Sed()
