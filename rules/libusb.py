import xyz
import os
import shutil

class Libusb(xyz.BuildProtocol):
    pkg_name = 'libusb'
    def configure(self):
        if self.config['host'].endswith('darwin'):
            ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        else:
            ldflags = '{standard_ldflags}'
        env = {'LDFLAGS': ldflags}
        self.host_lib_configure(env=env)

rules = Libusb
