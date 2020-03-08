import argparse
import os
import sys

from dodo_commands.dependencies.get import funcy
from dodo_commands.framework.funcy import keep_truthy, str_split_at

cut_suffix, distinct = funcy.cut_suffix, funcy.distinct


class CommandLine:
    def __init__(self):
        self.input_args = None
        self.cleaned = None
        self.command_name = None
        self.is_help = False
        self.is_trace = False
        self.inferred_layer_paths = []
        self.expanded_layer_paths = []
        self.given_layer_paths = []
        self.more_given_layer_paths = []
        self.is_running_directly_from_script = False

    @property
    def layer_paths(self):
        return distinct(self.inferred_layer_paths + self.expanded_layer_paths +
                        self.given_layer_paths + self.more_given_layer_paths)

    @property
    def _split_input1(self):
        input1 = self.input_args[1] if len(self.input_args) > 1 else ""

        # When running directly from a script, then we know the command was not
        # prefixed with layer names.
        if self.is_running_directly_from_script:
            return '', cut_suffix(input1, '.py')
        return str_split_at(input1, input1.rfind('.') + 1)

    @property
    def raw_command_name(self):
        return self._split_input1[1]

    @property
    def raw_command_prefix(self):
        return self._split_input1[0]

    @property
    def layer_names(self):
        return distinct(keep_truthy()(self.raw_command_prefix.split('.')))

    def get_trace(self):
        args = [x for x in self.input_args if x != '--trace']
        args[1] = self.command_name
        args.extend(["--layer=%s" % x for x in self.layer_paths])
        return args

    @staticmethod
    def get(ctr):
        return ctr.command_line


def init_command_line(self):
    self.is_running_directly_from_script = '__DODO__' not in os.environ
    parser = argparse.ArgumentParser()
    args = (
        # If a dodo script was called directly via the python interpreter,
        # then add sys.executable to make all calls look similar
        [sys.executable, *sys.argv]
        if self.is_running_directly_from_script else
        #
        sys.argv)

    if '--help' in args:
        if not ('--' in args and args.index('--') < args.index('--help')):
            self.is_help = True
            args = [x for x in args if x != '--help']

    parser.add_argument('-L', '--layer', action='append')
    parser.add_argument('--trace', action='store_true')

    known_args, args = parser.parse_known_args(args)

    self.given_layer_paths = known_args.layer or []
    self.is_trace = known_args.trace
    self.input_args = args

    return self
