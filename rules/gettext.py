import xyz

class Gettext(xyz.BuildProtocol):
    pkg_name = 'gettext'
    deps = []

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Gettext()
