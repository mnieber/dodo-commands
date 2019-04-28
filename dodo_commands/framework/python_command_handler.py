import pkgutil
import os
import sys
import ruamel.yaml
import subprocess
import traceback
from importlib import import_module
from dodo_commands.framework.config import CommandPath, Paths
from dodo_commands.framework.command_map import CommandMapItem
from dodo_commands.framework.util import query_yes_no


class PythonCommandMapItem(CommandMapItem):
    def __init__(self, group):
        super().__init__(group, 'py')
        self.package_path = group


class PythonCommandHandler:
    def add_commands_to_map(self, config, command_map):
        command_path = CommandPath(config)
        command_path.extend_sys_path()
        for item in command_path.items:
            commands = [
                name for _, name, is_pkg in pkgutil.iter_modules([item])
                if not is_pkg and not name.startswith('_')
            ]
            for command_name in commands:
                command_map[command_name] = PythonCommandMapItem(
                    group=os.path.basename(item))

    def execute(self, command_map_item, command_name):
        def install_packages(meta_data_filename):
            """Pip install packages found in meta_data_filename."""
            with open(meta_data_filename) as f:
                meta_data = ruamel.yaml.round_trip_load(f.read())
                print("This command wants to install additional packages:\n")
                print(meta_data['requirements'])
                if query_yes_no("Install (yes), or abort (no)?"):
                    print("\n--- Installing from %s ---" % meta_data_filename)
                    pip = Paths().pip()
                    subprocess.check_call([pip, "install"] +
                                          meta_data['requirements'])
                    print("--- Done ---\n\n")
                else:
                    sys.exit(1)

        import_path = '%s.%s' % (command_map_item.package_path, command_name)
        if command_map_item.package_path in ("", None, "."):
            import_path = command_name

        try:
            import_module(import_path)
        except ImportError as e:
            try:
                base_path = import_module(
                    command_map_item.package_path).__path__[0]
                meta_data_filename = os.path.join(base_path,
                                                  command_name + ".meta")
                if os.path.exists(meta_data_filename):
                    install_packages(meta_data_filename)
                    import_module(import_path)
                else:
                    traceback.print_exc(e)
                    sys.exit(1)
            except ImportError as e:
                traceback.print_exc(e)
                sys.exit(1)
