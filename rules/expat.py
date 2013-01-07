import xyz

class Expat(xyz.BuildProtocol):
    pkg_name = 'expat'

    def configure(self, builder, config):
        builder.host_lib_configure(config=config)

rules = Expat()
