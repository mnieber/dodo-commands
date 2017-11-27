# noqa
from dodo_commands.system_commands import DodoCommand
from six.moves import configparser
import os


class Command(DodoCommand):  # noqa
    safe = False
    help = "Write a value of the global Dodo Command configuration"

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('key')
        parser.add_argument('val', nargs='?')

    def _config_filename(self):
        return os.path.expanduser("~/.dodo_commands/config")

    def _write_config(self, config):
        """Save configuration."""
        with open(self._config_filename(), "w") as f:
            config.write(f)

    def _read_config(self):
        """Save configuration."""
        config = configparser.ConfigParser()
        config.read(self._config_filename())
        return config

    def handle_imp(self, key, val, **kwargs):  # noqa
        config = self._read_config()
        if val:
            config.set("DodoCommands", key, val)
            self._write_config(config)
        else:
            print(config.get("DodoCommands", key))
