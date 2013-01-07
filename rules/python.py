import xyz
import os
import shutil
import time

data_dir = os.path.abspath(os.path.dirname(__file__))

class Python(xyz.BuildProtocol):
    pkg_name = 'python'

    def configure(self, builder, config):
        ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        builder.cross_configure('--disable-shared', config=config,
                                env={'LDFLAGS': ldflags})
        setup_dist = 'pySetup.dist.darwin'
        time.sleep(1)
        shutil.copy(os.path.join(data_dir, setup_dist), 'Modules/Setup')
        # Need to regen Makefile after updating Modules/Setup
        builder.cmd('make', 'Makefile', config=config)

    def install(self, builder, config):
        with xyz.chdir(config['build_dir']):
            builder.cmd('make', 'DESTDIR={install_dir_abs}',
                        'bininstall', 'inclinstall', 'libainstall', 'libinstall',
                        config=config)

rules = Python()
