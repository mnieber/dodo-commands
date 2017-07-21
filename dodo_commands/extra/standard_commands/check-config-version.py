"""Compare configuration version to version in original project config file."""
from . import DodoCommand
from dodo_commands.framework.util import bordered
import os
import sys
import ruamel.yaml
from semantic_version import Version


class Command(DodoCommand):  # noqa
    def _get_version(self, config_filename):
        with open(config_filename) as f:
            config = ruamel.yaml.round_trip_load(f.read())
        return config.get("ROOT", {}).get("version", "")

    def _partial_sem_version(self, version):
        v = Version(version)
        return Version("%s.%s" % (v.major, v.minor), partial=True)

    def handle_imp(self, **kwargs):  # noqa
        project_dir = self.get_config("/ROOT/project_dir", "")
        original_file = os.path.join(
            project_dir, "dodo_commands", "default_project", "config.yaml"
        )
        if not os.path.exists(original_file):
            return

        original_version = self._get_version(original_file)
        if not original_version:
            sys.stderr.write(
                "No version found in original file %s\n" % original_file
            )
            return

        copied_file = os.path.join(project_dir, "dodo_commands", "res", "config.yaml")
        copied_version = self._get_version(copied_file)
        if not copied_version:
            sys.stderr.write(
                "No version found in user managed file %s\n" % copied_file
            )
            return

        if (
            self._partial_sem_version(copied_version) <
            self._partial_sem_version(original_version)
        ):
            sys.stdout.write(bordered(
                'Configuration needs update (%s < %s). Tip: use "dodo diff ."\n'
                % (
                    copied_version,
                    original_version,
                )
            ))
            sys.stdout.write('\n')
