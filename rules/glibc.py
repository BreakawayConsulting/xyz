import xyz

#
# At this stage we are building glibc for a very restricted purpose.
# We do not intend to actually link at runtime against this library,
# however we _do_ really want the header files, and the symbol version
# information contained in the .so
#
# We are pulling a relatively old version of glibc to ensure maximal
# compatability for any other binary packages that we create.
#

class Glibc(xyz.Package):
    pkg_name = 'glibc'
    full_deps = []

    def configure(self):
        env = {'CFLAGS': '-U_FORTIFY_SOURCE -O2 -fno-stack-protector -g3'}
        self.host_lib_configure(env=env, enable_shared=True)

    def install(self):
        with xyz.chdir(self.config['build_dir']), xyz.umask(0o22):
            self.cmd('make', 'install_root={install_dir_abs}', 'install')

        self.rmtree('{eprefix_dir}', 'bin')
        self.rmtree('{eprefix_dir}', 'lib', 'gconv')
        self.rmtree('{eprefix_dir}', 'sbin')
        self.rmtree('{prefix_dir}', 'share', 'zoneinfo')
        self.rmtree('{prefix_dir}', 'share', 'i18n')
        self.rmtree('{prefix_dir}', 'share', 'locale')
        self.rmtree('{prefix_dir}', 'etc')
        self.strip_info_dir()

        for f in ['libc.so', 'libpthread.so']:
            fixup_so_file(self.j('{eprefix_dir}', 'lib', f))

rules = Glibc


def fixup_so_file(so_filename):
    with open(so_filename) as f:
        lines = list(f.readlines())

    for idx, l in enumerate(lines):
        if l.startswith("GROUP"):
            parts = l.split()
            new_parts = []
            for part in parts:
                if part.startswith('/'):
                    part = part.split('/')[-1]
                new_parts.append(part)
            lines[idx] = ' '.join(new_parts) + '\n'


    with open(so_filename, 'w') as f:
        for l in lines:
            f.write(l)
