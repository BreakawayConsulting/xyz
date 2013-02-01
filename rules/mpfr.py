import xyz

class Mpfr(xyz.Package):
    pkg_name = 'mpfr'
    deps = ['texinfo', 'gmp']
    configure = xyz.Package.host_lib_configure

rules = Mpfr
