import xyz

class Mpfr(xyz.BuildProtocol):
    pkg_name = 'mpfr'
    deps = ['texinfo', 'gmp']
    configure = xyz.BuildProtocol.host_lib_configure

rules = Mpfr
