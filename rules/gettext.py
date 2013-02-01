import xyz

class Gettext(xyz.Package):
    pkg_name = 'gettext'
    configure = xyz.BuildProtocol.host_lib_configure

rules = Gettext
