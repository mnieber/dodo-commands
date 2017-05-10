"""Script for activating/creating a project in the projects dir."""
import argparse
from six.moves import configparser
import os
import sys
import ruamel.yaml
from plumbum import local
import dodo_commands


def _make_executable(script_filename):
    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | 0o111)


dodo_template = """
import os
from os.path import abspath, dirname
import sys
from dodo_commands.framework import execute_from_command_line


if __name__ == "__main__":
    if not dirname(abspath(__file__)).endswith("env/bin"):
        sys.stderr.write(
            'Error: this script must be run from the env/bin directory'
        )
        sys.exit(1)

    os.environ["DODO_COMMANDS_PROJECT_DIR"] = abspath(
        dirname(dirname(dirname(dirname(__file__))))
    )
    execute_from_command_line(sys.argv)
"""


class Activator:
    """Creates and activates projects."""

    def _config_filename(self):
        return os.path.expanduser("~/.dodo_commands/config")

    def _config(self):
        """Get configuration."""
        config = configparser.ConfigParser()
        config.read(self._config_filename())
        return config

    def _write_config(self):
        """Save configuration."""
        with open(self._config_filename(), "w") as f:
            self.config.write(f)

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
                r'PS1="(%s) $PS1"' % self.project
            ))

        pip = local[os.path.join(self._dodo_commands_dir, "env/bin", "pip")]
        pip("install", "argcomplete", "plumbum", "ruamel.yaml", "six")

        python = local[os.path.join(self._dodo_commands_dir, "env/bin", "python")]
        site_packages_dir = python(
            "-c",
            "from distutils.sysconfig import get_python_lib; " +
            "print(get_python_lib())"
        )[:-1]
        os.symlink(
            os.path.dirname(dodo_commands.__file__),
            os.path.join(site_packages_dir, "dodo_commands")
        )

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

    def _create_dodo_script(self):
        """Install the dodo entry point script."""
        env_dir = os.path.join(self._dodo_commands_dir, "env/bin")
        dodo_file = os.path.join(env_dir, "dodo")
        with open(dodo_file, "w") as of:
            of.write('#!%s/python\n' % env_dir)
            of.write(dodo_template)
        _make_executable(dodo_file)

    def _create_res_dir(self):
        """Install the dir with dodo_commands resources."""
        res_dir = os.path.join(self._dodo_commands_dir, "res")
        os.makedirs(res_dir)
        config_filename = os.path.join(res_dir, "config.yaml")
        default_config = {
            'ROOT': {
                'command_path': [
                    ['~/.dodo_commands', 'default_commands/*']
                ],
                'version': '1.0.0'
            }
        }
        with open(config_filename, "w") as f:
            f.write(ruamel.yaml.round_trip_dump(default_config))

    def _create_project(self):
        self._report(
            "Creating project at location %s ..." % self._project_dir
        )
        self._create_res_dir()
        self._create_virtual_env()
        self._register_autocomplete()
        self._create_dodo_script()
        self._report(" done\n")
        return True

    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    @property
    def _project_dir(self):
        return os.path.expanduser(os.path.join(
            self.config.get("DodoCommands", "projects_dir"),
            self.project
        ))

    @property
    def _dodo_commands_dir(self):
        return os.path.join(self._project_dir, "dodo_commands")

    def run(self, project, latest, create):
        """Activate or create a project in the projects dir."""
        self.project = project
        self.config = self._config()
        latest_project = (
            self.config.get("DodoCommands", "latest_project")
            if self.config.has_option("DodoCommands", "latest_project") else
            ""
        )

        if latest:
            if self.project:
                self._report(
                    "Options --latest and <project> are mutually exclusive\n"
                )
                return
            self.project = latest_project
            if not self.project:
                self._report(
                    "There is no latest project\n"
                )
                return

        if create:
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

        if self.project != latest_project:
            self.config.set("DodoCommands", "latest_project", self.project)
            self._write_config()

        sys.stdout.write(
            "source " + os.path.join(
                self._dodo_commands_dir, "env/bin/activate\n"
            )
        )


def main():  # noqa
    parser = argparse.ArgumentParser()
    parser.add_argument('project', nargs='?')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--create', action="store_true")
    group.add_argument('--latest', action="store_true")

    args = parser.parse_args()
    Activator().run(args.project, args.latest, args.create)
