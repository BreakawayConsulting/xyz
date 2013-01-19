import xyz

class Ncurses(xyz.Package):
    pkg_name = 'ncurses'

    def configure(self):
        self.host_lib_configure('--with-shared', '--without-cxx-binding', enable_shared=True)

    def install(self):
        super().install()
        self.rmtree('{prefix_dir}', 'man')
        self.rmtree('{prefix_dir}', 'share', 'terminfo')
        self.rmtree('{prefix_dir}', 'share', 'tabset')
        self.rmtree('{eprefix_dir}', 'bin')


rules = Ncurses
