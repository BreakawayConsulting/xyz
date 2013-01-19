import xyz

class Gmp(xyz.BuildProtocol):
    pkg_name = 'gmp'
    deps = ['texinfo']
    configure = xyz.BuildProtocol.host_lib_configure

rules = Gmp
