import xyz

class Libffi(xyz.Package):
    pkg_name = 'libffi'
    configure = xyz.Package.host_lib_configure

rules = Libffi
