from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
from dodo_commands.framework.config import get_project_dir, get_global_config


def _args():
    parser = ArgumentParser(
        description="Show diff for a file in the Dodo Commands system directory."
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Show diff for this file'
    )
    parser.add_argument(
        '--project-name',
        help='Compare to files from an alternative project'
    )
    parser.add_argument(
        '--defaults-dir',
        help='Set the relative path to the default config files'
    )
    args = Dodo.parse_args(parser)
    return args


def _diff_tool():
    return get_global_config().get("settings", "diff_tool")


if Dodo.is_main(__name__):
    args = _args()
    file = args.file or '.'

    project_dir = get_project_dir()
    if not project_dir:
        raise CommandError("No active dodo commands project")

    default_project_path = os.path.join(
        project_dir, "dodo_commands", "default_project"
    )

    if args.defaults_dir:
        if os.path.exists(default_project_path):
            raise CommandError(
                "The --default-dir option was supplied, " +
                "but the symlink %s already exists"
                % default_project_path
            )

        target_dir = os.path.join(project_dir, args.defaults_dir)
        if not os.path.exists(target_dir):
            raise CommandError(
                "The --default-dir option was supplied, " +
                "but the target directory %s does not exist"
                % target_dir
            )

        Dodo.runcmd(["ln", "-s", target_dir, default_project_path])

    if args.project_name:
        ref_project_dir = os.path.abspath(
            os.path.join(project_dir, "..", args.project_name)
        )
        original_file = os.path.join(ref_project_dir, file)
        copied_file = os.path.join(project_dir, file)
    else:
        original_file = os.path.realpath(
            os.path.join(default_project_path, file)
        )
        copied_file = os.path.join(project_dir, "dodo_commands", "res", file)

    Dodo.runcmd([_diff_tool(), original_file, copied_file])
