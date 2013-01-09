import xyz
import os
import shutil

class Texinfo(xyz.BuildProtocol):
    pkg_name = 'texinfo'

    def configure(self, builder, config):
        # FIXME: doesn't understand --disable-shared (it isn't a lib, so no surprise there!)
        builder.host_lib_configure(config=config)

rules = Texinfo()
