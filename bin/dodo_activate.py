"""Script for activating/creating a project in the projects folder."""
import argparse
from six.moves import configparser
import glob
import os
import sys
import yaml

from plumbum import local
from plumbum.cmd import chmod, cp, sed, ln, touch


class Activator:
    """Creates and activates projects."""

    def _args(self):
        """Get command line args."""
        parser = argparse.ArgumentParser()
        parser.add_argument('project')
        parser.add_argument('--create', action="store_true")
        return parser.parse_args()

    def _config(self):
        """Get configuration."""
        config = configparser.ConfigParser()
        config.read(os.path.join(self.source_folder, "dodo_commands.config"))
        return config

    def _create_virtual_env(self):
        """Install a virtual env."""
        local["virtualenv"](os.path.join(self.project_folder, "env"))

        # update activate script so that it shows the name of the
        # current project in the prompt
        activate_script = os.path.join(
            self.project_folder, "env/bin/activate"
        )
        with open(activate_script) as f:
            lines = f.read()
        with open(activate_script, "w") as f:
            f.write(lines.replace(
                r'PS1="(`basename \"$VIRTUAL_ENV\"`) $PS1"',
                r'PS1="(`dodo which`) $PS1"'
            ))

        pip = local[os.path.join(self.project_folder, "env/bin", "pip")]
        pip("install", "plumbum", "pudb", "PyYAML", "argcomplete")

    def _register_autocomplete(self):
        """Install a virtual env."""
        register = local[os.path.join(
            self.project_folder,
            "env/bin",
            "register-python-argcomplete"
        )]
        activate_script = os.path.join(
            self.project_folder,
            "env/bin",
            "activate"
        )
        (register >> activate_script)("dodo")

    def _create_framework_folder(self, dodo_commands_folder):
        """Install dodo commands framework into the virtual env bin folder."""
        ln(
            "-s",
            os.path.join(self.source_folder, "framework"),
            os.path.join(dodo_commands_folder, "framework")
        )

    def _create_dodo_script(self):
        """Install the dodo entry point script."""
        env_folder = os.path.join(self.project_folder, "env/bin")
        dodo_file = os.path.join(env_folder, "dodo")
        cp(
            os.path.join(self.source_folder, "bin", "dodo.py"),
            dodo_file,
        )
        chmod("+x", dodo_file)
        placeholder = "# SHEBANG_PLACEHOLDER_PLEASE_DONT_MODIFY_THIS_LINE"
        sed(
            '-i',
            's@%s@#!%s/python@g' % (placeholder, env_folder),
            dodo_file
        )

    def _create_default_commands(self, dodo_commands_folder):
        """Install the folder with the default commands."""
        ln(
            "-s",
            os.path.join(self.source_folder, "defaults", "commands"),
            os.path.join(dodo_commands_folder, "default_commands")
        )
        touch(os.path.join(dodo_commands_folder, "__init__.py"))

    def _create_defaults(self, dodo_commands_folder, project_name):
        """Install the folder with default projects."""
        for filename in glob.glob(
            os.path.join(
                self.source_folder, "defaults", "projects",
                "*", project_name, "*"
            )
        ):
            cp("-rf", filename, dodo_commands_folder)

        config_filename = os.path.join(dodo_commands_folder, "config.yaml")
        if not os.path.exists(config_filename):
            default_config = {
                'ROOT': {
                    'command_path': [
                        'dodo_commands/default_commands/*'
                    ],
                    'version': '1.0.0'
                }
            }
            with open(config_filename, "w") as f:
                f.write(
                    yaml.dump(
                        default_config, default_flow_style=False, indent=4
                    )
                )

    def _create_project(self, project):
        dodo_commands_folder = os.path.join(
            self.project_folder, "dodo_commands"
        )
        os.makedirs(dodo_commands_folder)
        self._create_virtual_env()
        self._register_autocomplete()
        self._create_defaults(dodo_commands_folder, project)
        self._create_framework_folder(dodo_commands_folder)
        self._create_dodo_script()
        self._create_default_commands(dodo_commands_folder)

    def run(self):
        """Activate or create a project in the projects folder."""
        bin_folder = os.path.dirname(__file__)
        self.source_folder = os.path.dirname(bin_folder)

        args = self._args()
        config = self._config()
        self.projects_folder = config.get("DodoCommands", "projects_folder")
        self.project_folder = os.path.join(self.projects_folder, args.project)

        def report(x):
            sys.stderr.write(x)

        if args.create:
            if os.path.exists(self.project_folder):
                report("Project already exists: %s\n" % self.project_folder)
                return
            report("Creating project at location %s ..." % self.project_folder)
            self._create_project(args.project)
            report(" done\n")
        elif not os.path.exists(self.project_folder):
            report(
                'Project not found: %s. Use the --create flag to create it\n'
                % self.project_folder
            )
            return

        sys.stdout.write(
            "source " + os.path.join(self.project_folder, "env/bin/activate\n")
        )
