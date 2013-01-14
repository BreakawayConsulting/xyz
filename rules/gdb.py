import xyz
import os
import shutil

class Gdb(xyz.BuildProtocol):
    crosstool = True
    pkg_name = 'gdb'
    supported_targets = ['arm-none-eabi']
    deps = ['texinfo', 'python']

    def check(self, config):
        target = config.get('target')
        if target not in self.supported_targets:
            raise xyz.UsageError("Invalid target ({}) for {}".format(target, self.pkg_name))

    def configure(self, builder, config):
        if config['host'].endswith('darwin'):
            ldflags = '{standard_ldflags} -F/Library/Frameworks -F/System/Library/Frameworks'
        else:
            ldflags = '{standard_ldflags}'

        builder.cross_configure('--disable-nls', '--enable-lto', '--enable-ld=yes', '--without-zlib',
                                 config=config, env={'LDFLAGS': ldflags})

        # After configuring we need to ice python, but we need
        # to ensure we do it using the built version of Python, not
        # this Python
        xyz.ensure_dir('gdb')
        with xyz.chdir('gdb'):
            builder.cmd('{devtree_dir_abs}/{host}/bin/python3', '{root_dir_abs}/ice/ice.py', 'stdlib', config=config)

rules = Gdb()
