import xyz

class Libffi(xyz.Package):
    pkg_name = 'libffi'
    configure = xyz.BuildProtocol.host_lib_configure

rules = Libffi
