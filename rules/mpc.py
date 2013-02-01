import xyz

class Mpc(xyz.Package):
    pkg_name = 'mpc'
    deps = ['texinfo', 'gmp', 'mpfr']
    configure = xyz.Package.host_lib_configure

rules = Mpc
