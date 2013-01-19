import xyz

class Sed(xyz.BuildProtocol):
    pkg_name = 'sed'
    configure = xyz.BuildProtocol.host_app_configure

rules = Sed
