import xyz

class Gettext(xyz.Package):
    pkg_name = 'gettext'
    configure = xyz.Package.host_lib_configure

rules = Gettext
