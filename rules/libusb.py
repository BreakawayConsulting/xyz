import xyz

class Libusb(xyz.Package):
    pkg_name = 'libusb'
    uses_osx_frameworks = True
    configure = xyz.Package.host_lib_configure

rules = Libusb
