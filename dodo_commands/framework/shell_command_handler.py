import os
import sys
from dodo_commands.framework.command_map import CommandMapItem


class ShellCommandMapItem(CommandMapItem):
    def __init__(self, group, filename):
        super(ShellCommandMapItem, self).__init__(group, filename, 'sh')


class ShellCommandHandler:
    def add_commands_to_map(self, command_path, file_map, command_map):
        for command_dir, files in file_map.items():
            for file in files:
                command_name, ext = os.path.splitext(os.path.basename(file))
                prefix = 'dodo.'
                if ext == '.sh' and command_name.startswith(prefix):
                    command_name = command_name[len(prefix):]
                    command_map[command_name] = ShellCommandMapItem(
                        group=os.path.basename(command_dir), filename=file)

    def execute(self, command_map_item, command_name):
        from dodo_commands.framework.singleton import Dodo
        Dodo.run([command_map_item.filename] + sys.argv[2:])
