import xyz

class Sed(xyz.Package):
    pkg_name = 'sed'
    configure = xyz.Package.host_app_configure

rules = Sed
