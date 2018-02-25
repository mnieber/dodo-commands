"""Compare configuration version to version in original project config file."""
from . import DodoCommand
from dodo_commands.framework import get_version
from dodo_commands.framework.util import bordered
from semantic_version import Version
import os
import ruamel.yaml
import sys


def _get_root_config_field(config_filename, field_name):
    with open(config_filename) as f:
        config = ruamel.yaml.round_trip_load(f.read())
    return config.get("ROOT", {}).get(field_name, "")


def _partial_sem_version(version):
    v = Version(version)
    return Version("%s.%s" % (v.major, v.minor), partial=True)


class Command(DodoCommand):  # noqa
    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            '--dodo',
            dest='check_dodo',
            action='store_true',
            help=(
                "Check that the installed dodo commands version satisfies the "
                "minimal dodo commands version in the dodo config "
                "(/ROOT/required_dodo_commands_version)"
            )
        )

        parser.add_argument(
            '--config',
            dest='check_config',
            action='store_true',
            help=(
                "Check that the version field in the local dodo commands config "
                "(/ROOT/version) is up-to-date with the version in the shared "
                "dodo commands config."
            )
        )

    def _config_filename(self):
        return os.path.join(
            self.get_config("/ROOT/project_dir", ""),
            "dodo_commands",
            "res",
            "config.yaml"
        )

    def check_dodo_commands_version(self):  # noqa
        required_version = _get_root_config_field(
            self._config_filename(), 'required_dodo_commands_version'
        )
        if required_version:
            actual_version = get_version()
            if Version(actual_version) < Version(required_version):
                sys.stdout.write(bordered(
                    'The dodo_commands package needs to be upgraded (%s < %s). Tip: use "dodo upgrade"'
                    % (
                        actual_version,
                        required_version,
                    ),
                ))
                sys.stdout.write('\n')

    def check_config_version(self):  # noqa
        project_dir = self.get_config("/ROOT/project_dir", "")
        original_file = os.path.join(
            project_dir, "dodo_commands", "default_project", "config.yaml"
        )
        if not os.path.exists(original_file):
            return

        original_version = _get_root_config_field(original_file, 'version')
        if not original_version:
            sys.stderr.write(
                "No version found in original file %s\n" % original_file
            )
            return

        copied_file = os.path.join(project_dir, "dodo_commands", "res", "config.yaml")
        copied_version = _get_root_config_field(copied_file, 'version')
        if not copied_version:
            sys.stderr.write(
                "No version found in user managed file %s\n" % copied_file
            )
            return

        if (
            _partial_sem_version(copied_version) <
            _partial_sem_version(original_version)
        ):
            sys.stdout.write(bordered(
                'Configuration needs update (%s < %s). Tip: use "dodo diff ."\n'
                % (
                    copied_version,
                    original_version,
                )
            ))
            sys.stdout.write('\n')

    def handle_imp(self, check_dodo, check_config, **kwargs):  # noqa
        if check_dodo:
            self.check_dodo_commands_version()
        if check_config:
            self.check_config_version()
