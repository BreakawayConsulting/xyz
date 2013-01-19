import xyz

class Expat(xyz.BuildProtocol):
    pkg_name = 'expat'
    configure = xyz.BuildProtocol.host_lib_configure

rules = Expat
