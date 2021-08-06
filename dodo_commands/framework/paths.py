import os


def _env():
    return os.environ.get("DODO_COMMANDS_ENV", "default")


class Paths:
    # Cached result of finding the current project dir
    _project_dir = None
    _config_dir = None

    def __init__(self):
        Paths._project_dir = Paths._project_dir or self.project_dir(_env())
        Paths._config_dir = Paths._config_dir or self.config_dir(_env())

    def home_dir(self, expanduser=True):
        return os.path.expanduser("~") if expanduser else "~"

    def envs_dir(self):
        return os.path.join(self.global_config_dir(), "envs")

    def env_dir(self, env=None):
        return os.path.join(self.envs_dir(), env or _env())

    def global_config_dir(self, expanduser=True):
        return os.path.join(self.home_dir(expanduser), ".dodo_commands")

    def global_config_filename(self):
        return os.path.join(self.global_config_dir(), "config")

    def default_config_mixin_filename(self):
        return os.path.join(self.global_config_dir(), "default_config.yaml")

    def default_project_dir(self, expanduser=True):
        return os.path.join(self.global_config_dir(expanduser), "default_project")

    def default_commands_dir(self, expanduser=True):
        return os.path.join(self.default_project_dir(), "commands")

    def global_commands_dir(self, expanduser=True):
        return os.path.join(self.global_config_dir(expanduser), "commands")

    def project_dir(self, env=None):
        """Return the root dir of the current project."""
        if env is None:
            return Paths._project_dir

        return os.path.realpath(os.path.join(self.env_dir(env), "project_dir"))

    def config_dir(self, env=None):
        if env is None:
            return Paths._config_dir

        return os.path.realpath(os.path.join(self.env_dir(env), "config_dir"))

    def package_dir(self):
        import dodo_commands

        return os.path.dirname(dodo_commands.__file__)

    def extra_dir(self):
        return os.path.join(self.package_dir(), "extra")
