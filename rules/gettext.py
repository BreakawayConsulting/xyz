import xyz

class Gettext(xyz.BuildProtocol):
    pkg_name = 'gettext'
    configure = xyz.BuildProtocol.host_lib_configure

rules = Gettext
