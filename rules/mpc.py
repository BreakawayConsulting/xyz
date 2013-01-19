import xyz
import os
import shutil

class Mpc(xyz.BuildProtocol):
    pkg_name = 'mpc'
    deps = ['texinfo', 'gmp', 'mpfr']
    configure = xyz.BuildProtocol.host_lib_configure

rules = Mpc
