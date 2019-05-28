"""Script for activating/creating a project in the projects dir."""
from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import (load_global_config_parser,
                                            write_global_config_parser, Paths)
from dodo_commands.framework.util import is_windows, symlink
import os
import shutil
import sys
import ruamel.yaml
from plumbum import local
import dodo_commands


def _make_executable(script_filename):
    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | 0o111)


def dodo_template(python_path):
    return """#!{python_path}
import sys
from dodo_commands.framework import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
""".format(
        python_path=python_path,
        bin='Scripts' if is_windows() else 'bin',
        sep=os.sep)


def dodo_template_bat(python_path, dodo_path):
    return """
@ECHO OFF
{python_path} {dodo_path} %*
""".format(
        python_path=python_path, dodo_path=dodo_path)


class Activator:
    """Creates and activates projects."""

    def _virtual_env_filename(self, basename):
        return os.path.join(self.paths.virtual_env_bin_dir(), basename)

    def _create_virtual_env(self):
        """Install a virtual env."""
        try:
            local["virtualenv"]('--version')
        except:
            raise CommandError(
                "Could not find virtualenv, please install it first.")

        local["virtualenv"]("-p",
                            self.config.get("settings", "python_interpreter"),
                            self.paths.virtual_env_dir(), "--prompt",
                            self.project)

        local[self.paths.pip()](
            "install",
            "ansimarkup",
            "argcomplete",
            "parsimonious",
            "plumbum",
            "python-dotenv",
            "ruamel.yaml",
            "semantic_version",
            "six",
        )

        symlink(
            os.path.dirname(dodo_commands.__file__),
            os.path.join(self.paths.site_packages_dir(), "dodo_commands"))

    def _create_dodo_script(self):
        """Install the dodo entry point script."""
        dodo_file = self._virtual_env_filename('dodo')
        python_path = os.path.join(self.paths.virtual_env_bin_dir(), 'python')
        with open(dodo_file, "w") as of:
            of.write(dodo_template(python_path))
        _make_executable(dodo_file)

        marker_file = self._virtual_env_filename('.dodo_project_dir_marker')
        with open(marker_file, "w") as of:
            pass

        if is_windows():
            dd_file = self._virtual_env_filename('dd.bat')
            with open(dd_file, "w") as of:
                of.write(dodo_template_bat(python_path, dodo_file))

    def _create_res_dir(self):
        """Install the dir with dodo_commands resources."""
        res_dir = self.paths.res_dir()
        os.makedirs(res_dir)
        config_filename = os.path.join(res_dir, "config.yaml")
        default_config = {
            'ROOT': {
                'command_path': [
                    os.path.join(
                        self.paths.default_commands_dir(expanduser=False), '*')
                ],
                'version':
                '1.0.0'
            }
        }
        with open(config_filename, "w") as f:
            f.write(ruamel.yaml.round_trip_dump(default_config))

    def _dodo_commands_sub_dir(self):
        return os.path.join(self.paths.project_dir(), "dodo_commands")

    def _create_project(self):
        project_dir = self.paths.project_dir()
        remove_project_dir_on_failure = not os.path.exists(project_dir)

        try:
            self._create_res_dir()
            self._create_virtual_env()
            self._create_dodo_script()
        except:
            if remove_project_dir_on_failure:
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
            elif os.path.exists(self._dodo_commands_sub_dir()):
                shutil.rmtree(self._dodo_commands_sub_dir())
            self._report('\n')
            raise

    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    def _config_get(self, section, key, default=""):
        return (self.config.get(section, key) if self.config.has_option(
            section, key) else default)

    def run(self, project, latest, create):
        """Activate or create a project in the projects dir."""
        self.config = load_global_config_parser()

        if not self.config.has_section('recent'):
            self.config.add_section('recent')

        latest_project = self._config_get("recent", "latest_project")
        previous_project = self._config_get("recent", "previous_project")

        if project == '-':
            project = previous_project
            if not project:
                raise CommandError("There is no previous project")
        self.project = project

        if latest:
            if self.project:
                self._report(
                    "Options --latest and <project> are mutually exclusive\n")
                return
            self.project = latest_project
            if not self.project:
                self._report("There is no latest project\n")
                return

        self.paths = Paths(
            project_dir=os.path.expanduser(
                os.path.join(
                    self.config.get("settings", "projects_dir"), self.
                    project)))

        if create:
            project_dir = self.paths.project_dir()

            if os.path.exists(self._dodo_commands_sub_dir()):
                self._report("Project already exists: %s\n" % project_dir)
                return False

            self._report("Creating project at location %s ..." % project_dir)
            self._create_project()
            self._report(" done\n")
        elif not os.path.exists(self.paths.project_dir()):
            raise CommandError(
                'Project not found: %s. Use the --create flag to create it\n' %
                self.paths.project_dir())

        if self.project != latest_project:
            self.config.set("recent", "previous_project", latest_project)
            self.config.set("recent", "latest_project", self.project)
            write_global_config_parser(self.config)

        sys.stdout.write(
            "source %s\n" % self._virtual_env_filename("activate"))


def _args():
    parser = ArgumentParser()
    parser.add_argument('project', nargs='?')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--latest', action="store_true")
    group.add_argument('--create', action="store_true")
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=False):
    args = _args()
    if not args.project and not args.latest:
        raise CommandError("No project was specified")
    Activator().run(args.project, args.latest, args.create)
