import xyz

class Expat(xyz.Package):
    pkg_name = 'expat'
    configure = xyz.Package.host_lib_configure

rules = Expat
