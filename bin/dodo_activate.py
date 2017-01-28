"""Script for activating/creating a project in the projects dir."""
import argparse
from six.moves import configparser
import glob
import os
import shutil
import sys
import yaml
from plumbum import local


def _make_executable(script_filename):
    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | 0o111)


def _touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


dodo_template = """
from os.path import dirname, abspath
import sys

if __name__ == "__main__":
    if not dirname(abspath(__file__)).endswith("env/bin"):
        sys.stderr.write(
            'Error: this script must be run from the env/bin directory'
        )
        sys.exit(1)

    project_dir = abspath(dirname(dirname(dirname(dirname(__file__)))))
    sys.path.append(project_dir)

    from dodo_commands import execute_from_command_line
    execute_from_command_line(sys.argv)
"""


class Activator:
    """Creates and activates projects."""

    def _args(self):
        """Get command line args."""
        parser = argparse.ArgumentParser()
        parser.add_argument('project')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--create', action="store_true")
        group.add_argument('--create-from')
        return parser.parse_args()

    def _config(self):
        """Get configuration."""
        config = configparser.ConfigParser()
        config.read("~/.dodo_commands")
        return config

    def _create_virtual_env(self):
        """Install a virtual env."""
        local["virtualenv"](
            "-p", self.config.get("DodoCommands", "python_interpreter"),
            os.path.join(self._dodo_commands_dir, "env")
        )

        # update activate script so that it shows the name of the
        # current project in the prompt
        activate_script = os.path.join(
            self._dodo_commands_dir, "env/bin/activate"
        )
        with open(activate_script) as f:
            lines = f.read()
        with open(activate_script, "w") as f:
            f.write(lines.replace(
                r'PS1="(`basename \"$VIRTUAL_ENV\"`) $PS1"',
                r'PS1="(`dodo which`) $PS1"'
            ))

        pip = local[os.path.join(self._dodo_commands_dir, "env/bin", "pip")]
        pip("install", "plumbum", "pudb", "PyYAML", "argcomplete", "six")

    def _register_autocomplete(self):
        """Install a virtual env."""
        register = local[os.path.join(
            self._dodo_commands_dir,
            "env/bin",
            "register-python-argcomplete"
        )]
        activate_script = os.path.join(
            self._dodo_commands_dir,
            "env/bin",
            "activate"
        )
        (register >> activate_script)("dodo")

    def _create_framework_dir(self):
        """Install dodo commands framework into the virtual env bin dir."""
        os.symlink(
            os.path.join(self._source_dir, "framework"),
            os.path.join(self._dodo_commands_dir, "framework")
        )

    def _create_dodo_script(self):
        """Install the dodo entry point script."""
        env_dir = os.path.join(self._dodo_commands_dir, "env/bin")
        dodo_file = os.path.join(env_dir, "dodo")
        with open(dodo_file, "w") as of:
            of.write('#!%s/python\n' % env_dir)
            of.write(dodo_template)

        _make_executable(dodo_file)

    def _create_default_commands(self):
        """Install the dir with the default commands."""
        os.symlink(
            os.path.join(self._source_dir, "defaults", "commands"),
            os.path.join(self._dodo_commands_dir, "defaults", "commands")
        )
        _touch(os.path.join(self._dodo_commands_dir, "__init__.py"))

    def _find_defaults_dir(self):
        if self.args.create_from and '/' in self.args.create_from:
            pattern = self.args.create_from
        elif self.args.create_from:
            pattern = os.path.join("*", self.args.create_from)
        else:
            pattern = os.path.join("*", self._project_name)

        candidates = glob.glob(os.path.join(
            self._source_dir, "defaults", "projects", pattern
        ))
        if len(candidates) > 1:
            self._report(
                "Source location for %s is ambigious, could be:\n"
                % self._project_name
            )
            self._report("\n".join(candidates))
            return None, False

        if len(candidates) == 0 and self.args.create_from:
            self._report(
                "Could not find a source location matching %s\n"
                % self.args.create_from
            )
            return None, False

        return (candidates[0] if candidates else None), True

    def _create_defaults(self, defaults_dir):
        """Install the dir with default projects."""
        os.mkdir(os.path.join(self._dodo_commands_dir, "defaults"))
        os.mkdir(os.path.join(self._dodo_commands_dir, "res"))

        res_dir = os.path.join(self._dodo_commands_dir, "res")
        if defaults_dir:
            for filename in glob.glob(os.path.join(defaults_dir, "*")):
                shutil.copytree(filename, res_dir)
            os.symlink(
                defaults_dir,
                os.path.join(self._dodo_commands_dir, "defaults/project")
            )
        else:
            config_filename = os.path.join(res_dir, "config.yaml")
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

    def _create_project(self):
        defaults_dir, has_defaults_dir = self._find_defaults_dir()
        if not has_defaults_dir:
            return False

        self._report(
            "Creating project at location %s ..." % self._project_dir
        )
        os.makedirs(self._dodo_commands_dir)
        self._create_defaults(defaults_dir)
        self._create_virtual_env()
        self._register_autocomplete()
        self._create_framework_dir()
        self._create_dodo_script()
        self._create_default_commands()
        self._report(" done\n")
        return True

    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    @property
    def _source_dir(self):
        bin_dir = os.path.dirname(__file__)
        return os.path.dirname(bin_dir)

    @property
    def _project_dir(self):
        return os.path.join(
            self.config.get("DodoCommands", "projects_dir"),
            self.args.project
        )

    @property
    def _dodo_commands_dir(self):
        return os.path.join(self._project_dir, "dodo_commands")

    @property
    def _project_name(self):
        return self.args.project

    def run(self):
        """Activate or create a project in the projects dir."""
        self.args = self._args()
        self.config = self._config()

        if self.args.create or self.args.create_from:
            if os.path.exists(self._dodo_commands_dir):
                self._report(
                    "Project already exists: %s\n" % self._project_dir
                )
                return
            if not self._create_project():
                return
        elif not os.path.exists(self._project_dir):
            self._report(
                'Project not found: %s. Use the --create flag to create it\n'
                % self._project_dir
            )
            return

        sys.stdout.write(
            "source " + os.path.join(
                self._dodo_commands_dir, "env/bin/activate\n"
            )
        )


def main():  # noqa
    Activator().run()
