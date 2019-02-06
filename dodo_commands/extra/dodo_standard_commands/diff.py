from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
import os
from dodo_commands.framework.config import load_global_config_parser, Paths


def _args():
    parser = ArgumentParser(
        description=
        "Show diff for a file in the Dodo Commands system directory.")
    parser.add_argument('file', nargs='?', help='Show diff for this file')
    parser.add_argument(
        '--project-name', help='Compare to files from an alternative project')
    args = Dodo.parse_args(parser)
    return args


def _diff_tool():
    return load_global_config_parser().get("settings", "diff_tool")


if Dodo.is_main(__name__):
    args = _args()
    file = args.file or '.'

    project_dir = Paths().project_dir()
    if not project_dir:
        raise CommandError("No active dodo commands project")

    if args.project_name:
        ref_project_dir = os.path.abspath(
            os.path.join(project_dir, "..", args.project_name))
        original_file = os.path.join(ref_project_dir, file)
        copied_file = os.path.join(project_dir, file)
    else:
        shared_config_dir = Dodo.get_config('/ROOT/shared_config_dir')
        original_file = os.path.realpath(os.path.join(shared_config_dir, file))
        copied_file = os.path.join(Paths().res_dir(), file)

    Dodo.run([_diff_tool(), original_file, copied_file])
