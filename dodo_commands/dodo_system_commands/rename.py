from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import projects_dir, Paths
from dodo_commands.framework.util import is_using_system_dodo
import os


def _args():
    parser = ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("new_project_name")
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if not is_using_system_dodo():
        raise CommandError(
            "Please deactivate your dodo project first by running 'deactivate'."
        )

    old_project_dir = os.path.join(projects_dir(), args.project_name)
    if not os.path.exists(old_project_dir):
        raise CommandError("Project dir not found: %s" % old_project_dir)
    old_paths = Paths(old_project_dir)

    new_project_dir = os.path.join(projects_dir(), args.new_project_name)
    if os.path.exists(new_project_dir):
        raise CommandError(
            "New project dir already exists: %s" % new_project_dir)
    new_paths = Paths(new_project_dir)

    Dodo.run(['mv', old_project_dir, new_project_dir], cwd='.')

    def fn(x):
        return os.path.join(new_paths.virtual_env_bin_dir(), x)

    replace_project_dir = 's#%s#%s#g' % (old_project_dir, new_project_dir)
    for script in (fn('dodo'), fn('activate')):
        Dodo.run(['sed', '-i', '-e', replace_project_dir, script], cwd='.')

    replace_prompt = 's#PS1="(%s) $PS1\"#PS1="(%s) $PS1"#g' % (
        args.project_name, args.new_project_name)
    Dodo.run(['sed', '-i', '-e', replace_prompt, fn('activate')], cwd='.')
