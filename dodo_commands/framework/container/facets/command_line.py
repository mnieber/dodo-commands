import os
import sys

from dodo_commands.framework import ramda as R


class CommandLine:
    def __init__(self):
        self.input_args = (
            [sys.executable] if self.is_running_directly_from_script else []
        ) + list(sys.argv)
        self.is_trace = False
        self.is_help = False
        self.layer_paths_from_command_prefix = []
        self.layer_paths_from_input_args = []
        self.decorators_from_input_args = []
        self.env_vars_from_input_args = []
        self.cwd = None

    @property
    def is_running_directly_from_script(self):
        return "__DODO__" not in os.environ

    @property
    def target_paths(self):
        return R.uniq(
            self.layer_paths_from_command_prefix + self.layer_paths_from_input_args
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
        return self._split_input1[1] or "help"

    @property
    def command_prefix(self):
        return self._split_input1[0]

    def get_trace(self):
        args = [x for x in self.input_args if x != "--trace"]
        args[1] = self.command_name
        args.extend(["--layer=%s" % x for x in self.target_paths])
        return args

    @staticmethod
    def get(ctr):
        return ctr.command_line
