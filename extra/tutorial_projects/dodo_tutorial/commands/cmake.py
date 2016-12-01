"""Configure code with CMake."""
from dodo_commands.default_commands.standard_commands import DodoCommand

class Command(DodoCommand):  # noqa
    decorators = ['docker']

    def _get_variable_list(self, prefix):
        return [
            prefix + "%s=%s" % key_val for key_val in
            self.get_config('/CMAKE/variables').items()
        ]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            ["cmake"] +
            self._get_variable_list("-D") +
            [self.get_config("/ROOT/src_dir")],
            cwd=self.get_config("/ROOT/build_dir")
        )
