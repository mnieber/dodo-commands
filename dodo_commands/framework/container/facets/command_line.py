import os
import sys

from dodo_commands.framework import ramda as R


class CommandLine:
    def __init__(self):
        self.input_args = None
        self.is_trace = False
        self.inferred_layer_paths = []
        self.expanded_layer_paths = []
        self.given_layer_paths = []
        self.more_given_layer_paths = []

    @property
    def is_running_directly_from_script(self):
        return "__DODO__" not in os.environ

    @property
    def is_help(self):
        return "--help" in sys.argv and not (
            "--" in sys.argv and sys.argv.index("--") < sys.argv.index("--help")
        )

    @property
    def layer_paths(self):
        return R.uniq(
            self.inferred_layer_paths
            + self.expanded_layer_paths
            + self.given_layer_paths
            + self.more_given_layer_paths
        )

    @property
    def _split_input1(self):
        input1 = self.input_args[1] if len(self.input_args) > 1 else ""

        # When running directly from a script, then we know the command was not
        # prefixed with layer names.
        if self.is_running_directly_from_script:
            return "", R.cut_suffix(input1, ".py")

        return R.split(input1.rfind(".") + 1)(input1)

    @property
    def command_name(self):
        return self._split_input1[1]

    @property
    def layer_names(self):
        command_prefix = self._split_input1[0]
        return R.uniq(R.filter(bool)(command_prefix.split(".")))

    def get_trace(self):
        args = [x for x in self.input_args if x != "--trace"]
        args[1] = self.command_name
        args.extend(["--layer=%s" % x for x in self.layer_paths])
        return args

    @staticmethod
    def get(ctr):
        return ctr.command_line
