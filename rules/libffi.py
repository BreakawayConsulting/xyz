import xyz
import os
import shutil

class Libffi(xyz.BuildProtocol):
    pkg_name = 'libffi'
    configure = xyz.BuildProtocol.host_lib_configure

rules = Libffi
