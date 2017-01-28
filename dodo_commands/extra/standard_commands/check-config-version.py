"""Compare configuration version to version in original project config file."""
from . import DodoCommand
import os
import sys
import yaml


class Command(DodoCommand):  # noqa
    def _get_version(self, config_filename):
        with open(config_filename) as f:
            config = yaml.load(f.read())
        version = config.get("ROOT", {}).get("version", "").split(".")
        return [x for x in version if x != ""]

    def handle_imp(self, **kwargs):  # noqa
        project_dir = self.get_config("/ROOT/project_dir", "")
        res_dir = os.path.join(project_dir, "dodo_commands", "res")
        original_file = os.path.join(
            project_dir, "dodo_commands", "default_project", "config.yaml"
        )
        original_version = self._get_version(original_file)
        if not original_version:
            sys.stderr.write(
                "No version found in original file %s\n" % original_file
            )
            return

        copied_file = os.path.join(res_dir, "config.yaml")
        copied_version = self._get_version(copied_file)
        if not copied_version:
            sys.stderr.write(
                "No version found in user managed file %s\n" % copied_file
            )
            return

        if copied_version[:2] < original_version[:2]:
            sys.stdout.write(
                "Configuration needs update (%s.%s < %s.%s)\n"
                % (
                    copied_version[0],
                    copied_version[1],
                    original_version[0],
                    original_version[1]
                )
            )
