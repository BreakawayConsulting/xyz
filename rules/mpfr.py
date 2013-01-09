import xyz
import os
import shutil

class Mpfr(xyz.BuildProtocol):
    pkg_name = 'mpfr'
    deps = ['texinfo', 'gmp']

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Mpfr()
