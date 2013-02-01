import xyz

class Gmp(xyz.Package):
    pkg_name = 'gmp'
    deps = ['texinfo']
    configure = xyz.Package.host_lib_configure

rules = Gmp
