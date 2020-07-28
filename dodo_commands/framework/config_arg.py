import sys

from dodo_commands.framework.config_key import Key


class ConfigArg:
    def __init__(self, config_key, *args, **kwargs):
        self.config_key = config_key
        self.args = args
        self.kwargs = kwargs

    @property
    def arg_name(self):
        return self.args[0].strip("-").replace("-", "_")

    def _key(self, config):
        return Key(config, self.config_key)

    def exists(self, config):
        return self._key(config).exists()

    def get(self, config):
        return self._key(config).get()



def add_config_args(parser, config, config_args):
    show_help = "--help" in sys.argv

    for config_arg in config_args or []:
        key_exists = config_arg.exists(config)

        if show_help or not key_exists:
            kwargs = dict(config_arg.kwargs)
            help_text = kwargs.get("help") or ""
            sep = ". " if help_text else ""
            if key_exists:
                value = str(config_arg.get(config))
                formatted_value = value[:50] + (value[50:] and "...")
                extra_help = "Read from config: %s = %s." % (
                    config_arg.config_key,
                    formatted_value,
                )
            else:
                extra_help = "Configuration key is %s" % config_arg.config_key

            kwargs["help"] = help_text + sep + extra_help
            parser.add_argument(*config_arg.args, **kwargs)
