import xyz
import os
import shutil
import time
import struct

data_dir = os.path.abspath(os.path.dirname(__file__))

class Python(xyz.BuildProtocol):
    pkg_name = 'python'

    def configure(self):
        if self.config['host'].endswith('darwin'):
            setup_dist = 'pySetup.dist.darwin'
            ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        elif self.config['host'].endswith('linux-gnu'):
            setup_dist = 'pySetup.dist.linux'
            ldflags = '{standard_ldflags}'
        else:
            raise UsageError("Host for python package must be on darwin or linux-gnu (not {})".format(self.config['host']))

        self.host_lib_configure(env={'LDFLAGS': ldflags})
        time.sleep(1)
        shutil.copy(os.path.join(data_dir, setup_dist), 'Modules/Setup')
        # Need to regen Makefile after updating Modules/Setup
        self.cmd('make', 'Makefile')

    def install(self):
        with xyz.chdir(self.config['build_dir']), xyz.umask(0o022):
            self.cmd('make', 'DESTDIR={install_dir_abs}',
                        'bininstall', 'inclinstall', 'libainstall', 'libinstall')

        for root, _, files in os.walk(self.config['install_dir']):
            for f in files:
                if not (f.endswith('.pyc') or f.endswith('.pyo')):
                    continue
                with open(os.path.join(root, f), 'r+b') as outf:
                    outf.seek(4)
                    outf.write(struct.pack('I', xyz.BASE_TIME))

        # Remove lib2to3
        lib_2to3 = self.j('{install_dir}', 'noprefix', 'lib', 'python3.3', 'lib2to3')
        xyz.rmtree(lib_2to3)

        for f in ['2to3', 'idle3', 'pydoc3', 'pyvenv']:
            bin_fn = self.j('{install_dir}', 'noprefix', '{host}', 'bin', f)
            os.unlink(bin_fn)

rules = Python
