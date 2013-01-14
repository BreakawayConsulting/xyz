import xyz
import os
import shutil
import time
import struct

data_dir = os.path.abspath(os.path.dirname(__file__))

class Python(xyz.BuildProtocol):
    pkg_name = 'python'

    def configure(self, builder, config):
        ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        builder.host_lib_configure('--disable-shared', config=config,
                                env={'LDFLAGS': ldflags})
        if config['host'].endswith('darwin'):
            setup_dist = 'pySetup.dist.darwin'
        elif config['host'].endswith('linux-gnu'):
            setup_dist = 'pySetup.dist.linux'
        else:
            raise UsageError("Host for python package must be on darwin or linux-gnu (not {})".format(config['host']))
        time.sleep(1)
        shutil.copy(os.path.join(data_dir, setup_dist), 'Modules/Setup')
        # Need to regen Makefile after updating Modules/Setup
        builder.cmd('make', 'Makefile', config=config)

    def install(self, builder, config):
        with xyz.chdir(config['build_dir']), xyz.umask(0o022):
            builder.cmd('make', 'DESTDIR={install_dir_abs}',
                        'bininstall', 'inclinstall', 'libainstall', 'libinstall',
                        config=config)

        for root, _, files in os.walk(config['install_dir']):
            for f in files:
                if not (f.endswith('.pyc') or f.endswith('.pyo')):
                    continue
                with open(os.path.join(root, f), 'r+b') as outf:
                    outf.seek(4)
                    outf.write(struct.pack('I', xyz.BASE_TIME))

rules = Python()
