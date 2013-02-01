import xyz

class Sed(xyz.Package):
    pkg_name = 'sed'
    configure = xyz.BuildProtocol.host_app_configure

rules = Sed
