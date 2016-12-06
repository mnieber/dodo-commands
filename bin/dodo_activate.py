"""Script for activating/creating a project in the projects dir."""
import argparse
from six.moves import configparser
import glob
import os
import sys
import yaml

from plumbum import local
from plumbum.cmd import chmod, cp, ln, sed, touch


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
        config_path = os.path.join(self.source_dir, "dodo_commands.config")
        config.read(config_path)
        return config

    def _create_virtual_env(self):
        """Install a virtual env."""
        local["virtualenv"](
            "-p", self.python_interpreter,
            os.path.join(self.project_dir, "env")
        )

        # update activate script so that it shows the name of the
        # current project in the prompt
        activate_script = os.path.join(
            self.project_dir, "env/bin/activate"
        )
        with open(activate_script) as f:
            lines = f.read()
        with open(activate_script, "w") as f:
            f.write(lines.replace(
                r'PS1="(`basename \"$VIRTUAL_ENV\"`) $PS1"',
                r'PS1="(`dodo which`) $PS1"'
            ))

        pip = local[os.path.join(self.project_dir, "env/bin", "pip")]
        pip("install", "plumbum", "pudb", "PyYAML", "argcomplete", "six")

    def _register_autocomplete(self):
        """Install a virtual env."""
        register = local[os.path.join(
            self.project_dir,
            "env/bin",
            "register-python-argcomplete"
        )]
        activate_script = os.path.join(
            self.project_dir,
            "env/bin",
            "activate"
        )
        (register >> activate_script)("dodo")

    def _create_framework_dir(self, dodo_commands_dir):
        """Install dodo commands framework into the virtual env bin dir."""
        ln(
            "-s",
            os.path.join(self.source_dir, "framework"),
            os.path.join(dodo_commands_dir, "framework")
        )

    def _create_dodo_script(self):
        """Install the dodo entry point script."""
        env_dir = os.path.join(self.project_dir, "env/bin")
        dodo_file = os.path.join(env_dir, "dodo")
        cp(
            os.path.join(self.source_dir, "bin", "dodo.py"),
            dodo_file,
        )
        chmod("+x", dodo_file)
        placeholder = "# SHEBANG_PLACEHOLDER_PLEASE_DONT_MODIFY_THIS_LINE"
        sed(
            '-i',
            's@%s@#!%s/python@g' % (placeholder, env_dir),
            dodo_file
        )

    def _create_default_commands(self, dodo_commands_dir):
        """Install the dir with the default commands."""
        ln(
            "-s",
            os.path.join(self.source_dir, "defaults", "commands"),
            os.path.join(dodo_commands_dir, "defaults", "commands")
        )
        touch(os.path.join(dodo_commands_dir, "__init__.py"))

    def _find_defaults_dir(self, dodo_commands_dir, project_name):
        """Install the dir with default projects."""
        pattern = (
            "{project_name}"
            if '/' in project_name else
            "*/{project_name}"
        ).format(project_name=project_name)

        candidates = glob.glob(os.path.join(
            self.source_dir, "defaults", "projects", pattern
        ))
        if len(candidates) > 1:
            sys.stderr.write(
                "Source location for %s is ambigious, could be:\n"
                % project_name
            )
            sys.stderr.write("\n".join(candidates))
            return None, False

        if len(candidates) == 0:
            return None, True

        return candidates[0], True

    def _create_defaults(self, dodo_commands_dir, defaults_dir):
        """Install the dir with default projects."""
        os.mkdir(os.path.join(dodo_commands_dir, "defaults"))
        if defaults_dir:
            for filename in glob.glob(os.path.join(defaults_dir, "*")):
                cp("-rf", filename, dodo_commands_dir)
            ln(
                "-s",
                defaults_dir,
                os.path.join(dodo_commands_dir, "defaults/project")
            )
        else:
            config_filename = os.path.join(dodo_commands_dir, "config.yaml")
            default_config = {
                'ROOT': {
                    'command_path': [
                        'dodo_commands/defaults/commands/*'
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
        dodo_commands_dir = os.path.join(
            self.project_dir, "dodo_commands"
        )
        defaults_dir, has_defaults_dir = self._find_defaults_dir(
            dodo_commands_dir, project
        )
        if not has_defaults_dir:
            return

        os.makedirs(dodo_commands_dir)
        self._create_defaults(dodo_commands_dir, defaults_dir)
        self._create_virtual_env()
        self._register_autocomplete()
        self._create_framework_dir(dodo_commands_dir)
        self._create_dodo_script()
        self._create_default_commands(dodo_commands_dir)

    def run(self):
        """Activate or create a project in the projects dir."""
        bin_dir = os.path.dirname(__file__)
        self.source_dir = os.path.dirname(bin_dir)

        args = self._args()
        config = self._config()
        self.projects_dir = config.get("DodoCommands", "projects_dir")
        self.python_interpreter = config.get(
            "DodoCommands", "python_interpreter"
        )
        self.project_dir = os.path.join(self.projects_dir, args.project)

        def report(x):
            sys.stderr.write(x)
            sys.stderr.flush()

        if args.create:
            if os.path.exists(self.project_dir):
                report("Project already exists: %s\n" % self.project_dir)
                return
            report("Creating project at location %s ..." % self.project_dir)
            self._create_project(args.project)
            report(" done\n")
        elif not os.path.exists(self.project_dir):
            report(
                'Project not found: %s. Use the --create flag to create it\n'
                % self.project_dir
            )
            return

        sys.stdout.write(
            "source " + os.path.join(self.project_dir, "env/bin/activate\n")
        )
