import xyz

class Texinfo(xyz.Package):
    pkg_name = 'texinfo'

    def configure(self):
        self.host_app_configure('--disable-nls')

rules = Texinfo
