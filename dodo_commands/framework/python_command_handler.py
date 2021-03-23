import os
import re
import subprocess
import sys
from importlib import import_module

from dodo_commands.dependencies import yaml_round_trip_load
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.command_map import CommandMapItem
from dodo_commands.framework.command_path import extend_sys_path
from dodo_commands.framework.config import Paths
from dodo_commands.framework.util import query_yes_no

try:
    import_error_type = ImportError
except Exception as e:
    import_error_type = ModuleNotFoundError

CommandNotFound = plumbum.commands.processes.CommandNotFound


class PythonCommandMapItem(CommandMapItem):
    def __init__(self, group, filename):
        super(PythonCommandMapItem, self).__init__(group, filename, "py")
        self.package_path = group


class PythonCommandHandler:
    def add_commands_to_map(self, command_dirs, file_map, command_map):
        extend_sys_path(command_dirs)
        for command_dir, files in file_map.items():
            for file in files:
                command_name, ext = os.path.splitext(os.path.basename(file))
                if ext == ".py" and not command_name.startswith("_"):
                    command_map[command_name] = PythonCommandMapItem(
                        group=os.path.basename(command_dir), filename=file
                    )

    def execute(self, command_map_item, command_name):
        def meta_data_filename():
            base_path = os.path.dirname(command_map_item.filename)
            return os.path.join(base_path, command_name + ".meta")

        def meta_data():
            if os.path.exists(meta_data_filename()):
                with open(meta_data_filename()) as f:
                    return yaml_round_trip_load(f.read())
            return None

        def install_python_packages(meta_data, dependency):
            """Pip install packages found in meta_data."""
            requirements = [
                x
                for x in meta_data["requirements"]
                if re.search(r"\b" + dependency + r"\b", x)
            ]
            if requirements:
                if len(requirements) > 1:
                    raise CommandError(
                        "Found more than 1 candidate for python package %s in %s"
                        % (dependency, meta_data_filename())
                    )

                requirement = requirements[0]
                print("This command wants to install %s:\n" % requirement)
                if query_yes_no("Install (yes), or abort (no)?"):
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", requirement]
                    )
                    print("--- Done ---\n\n")

        import_path = "%s.%s" % (command_map_item.package_path, command_name)
        if command_map_item.package_path in ("", None, "."):
            import_path = command_name

        # Try the import, return if success
        try:
            return import_module(import_path)
        except import_error_type as e:
            # Try the import again, but first run install_python_packages
            dependency = e.name
            try:
                md = meta_data()
                if md:
                    install_python_packages(md, dependency)
                import_module(import_path)
            except import_error_type as e:
                raise CommandError("Could not import python module: %s" % dependency)
