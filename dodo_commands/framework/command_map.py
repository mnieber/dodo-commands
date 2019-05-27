from dodo_commands.framework.singleton import Dodo
from dodo_commands.framework.config import get_command_path
import glob
import os


class CommandMapItem(object):
    def __init__(self, group, filename, extension):
        self.group = group
        self.filename = filename
        self.extension = extension


def get_command_map(command_path=None):
    """
    Return a dictionary mapping command names to their Python module directory.
    The dictionary is in the format {command_name: module_name}.
    """
    from dodo_commands.framework.python_command_handler import PythonCommandHandler
    from dodo_commands.framework.yaml_command_handler import YamlCommandHandler
    from dodo_commands.framework.shell_command_handler import ShellCommandHandler

    command_path = command_path or get_command_path()
    command_map = {}

    file_map = {}
    for command_dir in command_path.items:
        file_map[command_dir] = list(
            glob.glob(os.path.join(command_dir, '*.*')))

    for handler in (PythonCommandHandler(), YamlCommandHandler(),
                    ShellCommandHandler()):
        handler.add_commands_to_map(command_path, file_map, command_map)

    return command_map


def execute_script(command_map, command_name):
    """
    Executes the script associated with command_name by importing its package.
    The script is assumed to have an entry point that is executed if
    Dodo.is_main(__name__) is True.
    """
    from dodo_commands.framework.python_command_handler import PythonCommandHandler
    from dodo_commands.framework.yaml_command_handler import YamlCommandHandler
    from dodo_commands.framework.shell_command_handler import ShellCommandHandler

    command_map_item = command_map[command_name]
    Dodo.command_name = command_name

    if command_map_item.extension == 'py':
        Dodo.package_path = command_map_item.package_path
        PythonCommandHandler().execute(command_map_item, command_name)
    elif command_map_item.extension == 'yaml':
        YamlCommandHandler().execute(command_map_item, command_name)
    elif command_map_item.extension == 'sh':
        ShellCommandHandler().execute(command_map_item, command_name)
    else:
        raise Exception("Logical error")
