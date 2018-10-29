import os
from plumbum import local


def _is_windows():
    return os.name == 'nt'


def _ext():
    return '.exe' if _is_windows() else ''


class Paths:
    def __init__(self, project_dir=None):
        self._project_dir = project_dir or os.environ.get(
            'DODO_COMMANDS_PROJECT_DIR')

    def home_dir(self):
        return os.path.expanduser('~')

    def global_config_dir(self):
        return os.path.join(self.home_dir(), '.dodo_commands')

    def global_config_filename(self):
        return os.path.join(self.global_config_dir(), 'config')

    def default_commands_dir(self):
        return os.path.join(self.global_config_dir(), 'default_commands')

    def virtual_env_dir(self):
        return os.path.join(self.project_dir(), 'dodo_commands', 'env')

    def virtual_env_bin_dir(self):
        return os.path.join(self.virtual_env_dir(), 'Scripts'
                            if _is_windows() else 'bin')

    def pip(self):
        return os.path.join(self.virtual_env_bin_dir(), 'pip' + _ext())

    def site_packages_dir(self):
        python = local[os.path.join(self.virtual_env_bin_dir(), "python" +
                                    _ext())]

        result = python("-c",
                        "from distutils.sysconfig import get_python_lib; " +
                        "print(get_python_lib())")
        while result[-1] in ['\n', '\r']:
            result = result[:-1]
        return result

    def project_dir(self):
        """Return the root dir of the current project."""
        return self._project_dir

    def res_dir(self):
        return os.path.join(self.project_dir(), "dodo_commands", "res")

    def package_dir(self):
        import dodo_commands
        return os.path.dirname(dodo_commands.__file__)

    def extra_dir(self):
        return os.path.join(self.package_dir(), "extra")
