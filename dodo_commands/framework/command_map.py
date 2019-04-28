from dodo_commands.framework.singleton import Dodo


class CommandMapItem:
    def __init__(self, group, extension):
        self.group = group
        self.extension = extension


def get_command_map(command_path):
    """
    Return a dictionary mapping command names to their Python module directory.
    The dictionary is in the format {command_name: module_name}.
    """
    from dodo_commands.framework.python_command_handler import PythonCommandHandler
    from dodo_commands.framework.yaml_command_handler import YamlCommandHandler

    command_map = {}
    PythonCommandHandler().add_commands_to_map(command_path, command_map)
    YamlCommandHandler().add_commands_to_map(command_path, command_map)
    return command_map


def execute_script(command_map, command_name):
    """
    Executes the script associated with command_name by importing its package.
    The script is assumed to have an entry point that is executed if
    Dodo.is_main(__name__) is True.
    """
    from dodo_commands.framework.python_command_handler import PythonCommandHandler
    from dodo_commands.framework.yaml_command_handler import YamlCommandHandler

    command_map_item = command_map[command_name]
    Dodo.command_name = command_name

    if command_map_item.extension == 'py':
        Dodo.package_path = command_map_item.package_path
        PythonCommandHandler().execute(command_map_item, command_name)
    elif command_map_item.extension == 'yaml':
        YamlCommandHandler().execute(command_map_item, command_name)
    else:
        raise Exception("Logical error")
