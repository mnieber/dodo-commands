import re
import os
import platform
import ruamel.yaml
import subprocess
from plumbum.commands.processes import CommandNotFound
from importlib import import_module
from dodo_commands.framework.config import Paths
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.command_map import CommandMapItem
from dodo_commands.framework.util import query_yes_no


class PythonCommandMapItem(CommandMapItem):
    def __init__(self, group, filename):
        super(PythonCommandMapItem, self).__init__(group, filename, 'py')
        self.package_path = group


class PythonCommandHandler:
    def add_commands_to_map(self, command_path, file_map, command_map):
        command_path.extend_sys_path()
        for command_dir, files in file_map.items():
            for file in files:
                command_name, ext = os.path.splitext(os.path.basename(file))
                if ext == '.py' and not command_name.startswith('_'):
                    command_map[command_name] = PythonCommandMapItem(
                        group=os.path.basename(command_dir), filename=file)

    def execute(self, command_map_item, command_name):
        def meta_data_filename():
            base_path = import_module(
                command_map_item.package_path).__path__[0]
            return os.path.join(base_path, command_name + ".meta")

        def meta_data():
            if os.path.exists(meta_data_filename()):
                with open(meta_data_filename()) as f:
                    return ruamel.yaml.round_trip_load(f.read())
            return None

        def install_packages(meta_data, dependency):
            """Pip install packages found in meta_data."""
            packager_name = 'brew' if platform.system() == 'Darwin' else 'apt'
            package_data = meta_data['packages'].get(packager_name, {})
            recipe = package_data.get(dependency, None)
            if recipe:
                commands = [recipe] if isinstance(recipe, str) else recipe

                print("This command wants to run:\n%s\n" % '\n'.join(commands))
                if query_yes_no("Install (yes), or abort (no)?"):
                    for package_cmd in commands:
                        subprocess.check_call(package_cmd.split())
                    print("--- Done ---\n\n")

        def install_python_packages(meta_data, dependency):
            """Pip install packages found in meta_data."""
            requirements = [
                x for x in meta_data['requirements']
                if re.search(r"\b" + dependency + r"\b", x)
            ]
            if requirements:
                if len(requirements) > 1:
                    raise CommandError(
                        "Found more than 1 candidate for python package %s in %s"
                        % (dependency, meta_data_filename()))

                requirement = requirements[0]
                print("This command wants to install %s:\n" % requirement)
                if query_yes_no("Install (yes), or abort (no)?"):
                    pip = Paths().pip()
                    subprocess.check_call([pip, "install", requirement])
                    print("--- Done ---\n\n")

        def get_program_from_exception(e):
            m = re.search(r"cannot import name '(\w+)' from 'plumbum.cmd'",
                          e.args[0]) if len(e.args) else None
            return m.groups(1)[0] if m else None

        import_path = '%s.%s' % (command_map_item.package_path, command_name)
        if command_map_item.package_path in ("", None, "."):
            import_path = command_name

        # Try the import, return if success
        try:
            return import_module(import_path)
        except ImportError as e:
            exception_type = type(e)
            program = get_program_from_exception(e)
            if program:
                dependency, install = program, install_packages
            else:
                dependency, install = e.name, install_python_packages
        except CommandNotFound as e:
            exception_type = type(e)
            dependency, install = e.name, install_python_packages

        # Try the import again, but first run install
        try:
            install(meta_data(), dependency)
            import_module(import_path)
        except exception_type:
            fail_msg = ('Could not find executable: %s' % dependency if
                        (install is install_packages) else
                        'Could not import python module: %s' % dependency)
            raise CommandError(fail_msg)
