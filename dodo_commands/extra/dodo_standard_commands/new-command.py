from argparse import ArgumentParser
import os

from six.moves import input as raw_input
from funcy.py2 import cut_prefix

from dodo_commands import Dodo, CommandError
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.choice_picker import ChoicePicker
from dodo_commands.framework.funcy import map_with


def _args():
    parser = ArgumentParser(description="Creates a new Dodo command.")
    parser.add_argument('-f',
                        '--force',
                        action='store_true',
                        help='Overwrite existing command script')
    args = Dodo.parse_args(parser)
    return args


def create_command_dir():
    def get_command_dir_name():
        while True:
            dir_name = raw_input("\nEnter a name for the commands dir: ")
            if dir_name:
                default_src_dir = os.path.join(
                    Dodo.get_config('/ROOT/project_dir'), 'src')
                src_dir = Dodo.get_config('/ROOT/src_dir', default_src_dir)
                return os.path.join(src_dir, "extra", "dodo_commands",
                                    dir_name)
            else:
                print("Sorry, I did not understand that.")

    def create_dir(new_command_dir):
        if not os.path.exists(new_command_dir):
            Dodo.run(['mkdir', '-p', new_command_dir])

        init_py = os.path.join(new_command_dir, '__init__.py')
        if not os.path.exists(init_py):
            Dodo.run(['touch', init_py])

    def save_config(new_command_dir):
        if not [
                x
                for x in command_dirs if os.path.normpath(x) == new_command_dir
        ]:
            config = ConfigIO().load()
            config['ROOT']['command_path'].append(new_command_dir)
            ConfigIO().save(config)

    command_dir = get_command_dir_name()
    create_dir(command_dir)
    save_config(command_dir)
    return command_dir


def get_command_dir(command_dirs):
    col_width = max(len(os.path.basename(x)) for x in command_dirs)

    def map_to_choice(command_dir):
        return "%s (%s)" % (os.path.basename(command_dir).ljust(col_width),
                            command_dir)

    def get_choice_idx0(choices):
        class Picker(ChoicePicker):
            def print_choices(self, choices):
                for idx, command_dir in enumerate(choices):
                    if idx == len(choices) - 1:
                        print("")
                    print("%d - %s" % (idx + 1, command_dir))
                print()

            def question(self):
                return "Select a target command dir: "

        picker = Picker(choices)
        picker.pick()
        return picker.get_idxs0()[0]

    choices = map_with(map_to_choice)(command_dirs) + [
        "create a new commands dir"
    ]
    choice_idx0 = get_choice_idx0(choices)
    if choice_idx0 == len(choices) - 1:
        return create_command_dir()
    return command_dirs[choice_idx0]


def get_parser_args(args):
    def get_choice_idxs0(args):
        class Picker(ChoicePicker):
            def print_choices(self, choices):
                print("0 - none")
                for idx, arg in enumerate(choices):
                    print("%d - %s" % (idx + 1, arg[1]))
                print()

            def question(self):
                return "Select the options and args that are given by the user: "

            def on_invalid_index(self, index):
                if index == 0:
                    self.idxs = []

        picker = Picker(args)
        picker.pick()
        return picker.get_idxs0()

    def convert_to_single_string(args, idxs):
        single_string = ""
        for idx in idxs:
            arg = args[idx]
            single_string += "    parser.add_argument('{name}')\n".format(
                name=arg[0])
        return single_string

    idxs0 = get_choice_idxs0(args)
    return idxs0, convert_to_single_string(args, idxs0)


def get_params(args, remaining_idxs):
    def get_choices(args):
        class Picker(ChoicePicker):
            def print_choices(self, choices):
                print("0 - none")
                for idx, command_dir in enumerate(choices):
                    if idx == len(choices) - 1:
                        print("")
                    print("%d - %s" % (idx + 1, command_dir))
                print()

            def question(self):
                return "Select the options and args that come from the config: "

            def maybe_handle_invalid_index(self, index):
                if index == 0:
                    self.idxs = []

        remaining_choices = [
            args[remaining_idx] for remaining_idx in remaining_idxs
        ]
        picker = Picker(remaining_choices)
        picker.pick()
        return [remaining_idxs[x] for x in picker.get_idxs0()]

    def convert_to_single_string(args, idxs):
        single_string = ""
        for idx in idxs:
            name = args[idx][0]
            clean_name = args[idx][2]
            single_string += (
                "        " +
                "ConfigArg('/PATH/TO/{clean_name}', '{name}')".format(
                    name=name, clean_name=clean_name))
        return single_string

    idxs = get_choices(args)
    return idxs, convert_to_single_string(args, idxs)


script = """from argparse import ArgumentParser

from dodo_commands import Dodo, ConfigArg, CommandError


def _args():
    parser = ArgumentParser(
        description='{description}'
    )

    # Add arguments to the parser here
{parser_args_str}
    # Parse the arguments.
    args = Dodo.parse_args(parser, config_args=[
{params_str}
    ])

    args.cwd = Dodo.get_config('/ROOT/project_dir')

    # Raise an error if something is not right
    if False:
        raise CommandError('Oops')

    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    Dodo.run([{args_str}], cwd=args.cwd)
"""

if Dodo.is_main(__name__, safe=False):
    parsed_args = _args()

    name = raw_input("Enter a name for the command: ")
    description = raw_input("Enter a description: ")

    def get_args():
        def map_to_split_arg(arg):
            arg_name = arg.split('=')[0]

            clean_name = arg_name
            clean_name = cut_prefix(clean_name, '--')
            clean_name = cut_prefix(clean_name, '-')

            return (arg_name, arg, clean_name)

        raw_args = raw_input("Enter a command line to run inside the script: ")
        raw_args = raw_args.split(' ')
        return map_with(map_to_split_arg)(raw_args)

    __import__('pudb').set_trace()
    command_dirs = Dodo.get_container().commands.command_dirs
    command_dir = get_command_dir(command_dirs)
    dest_path = os.path.join(command_dir, name + ".py")

    args = get_args()
    parser_arg_idxs, parser_args_str = get_parser_args(args)

    remaining_arg_idxs = [
        x for x in range(len(args)) if x not in parser_arg_idxs
    ]
    param_arg_idxs, params_str = get_params(args, remaining_arg_idxs)

    if os.path.exists(dest_path) and not parsed_args.force:
        raise CommandError("Destination already exists: %s" % dest_path)

    args_str_parts = []
    for idx in range(len(args)):
        arg = args[idx]
        if idx in parser_arg_idxs or idx in param_arg_idxs:
            args_str_parts.append("args." + arg[2])
        else:
            args_str_parts.append("'%s'" % arg[1])
    args_str = ", ".join(args_str_parts)

    with open(dest_path, "w") as f:
        f.write(
            script.format(parser_args_str=parser_args_str,
                          params_str=params_str,
                          description=description,
                          args_str=args_str))

    print(dest_path)
