"""Pull the latest version of the Dodo Commands system."""
from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import ConfigIO
import glob
import os
import sys


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        'src_dir',
        help="The src directory for the bootstrapped project"
    )
    parser.add_argument(
        'project_defaults_dir',
        help="Location relative to src_dir where the default project config is stored",
    )
    parser.add_argument('--force', dest="use_force", action="store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--git-url', dest='git_url',
        help="Clone this repository to the src_dir location",
    )
    group.add_argument(
        '--link-dir',
        help="Make the src directory a symlink to this directory",
    )
    group.add_argument(
        '--cookiecutter-url',
        help="Use cookiecutter to create the src_dir location",
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=0,
        help="Depth for cloning repositories"
    )
    parser.add_argument(
        '--branch',
        help="Branch to checkout after cloning"
    )

    parser.add_argument(
        '--src-subdir',
        help="Specify a subdirectory of src_dir to clone into",
    )

    args = Dodo.parse_args(parser)
    args.project_dir = Dodo.get_config('/ROOT/project_dir')
    return args


def _report(msg):
    sys.stderr.write(msg + "\n")


def _copy_defaults(args, project_defaults_dir):
    res_dir = os.path.join(args.project_dir, "dodo_commands", "res")
    for filename in glob.glob(os.path.join(project_defaults_dir, "*")):
        dest_path = os.path.join(res_dir, os.path.basename(filename))
        if os.path.exists(dest_path):
            if args.opt_confirm:
                print("Warning, destination path already exists: %s" % dest_path)
            elif args.use_force:
                print("Overwriting existing path: %s" % dest_path)
            else:
                raise CommandError(
                    "Destination path %s already exists. " % dest_path +
                    "Use the --confirm or --force flag to overwrite it."
                )
        Dodo.runcmd(["cp", "-rf", filename, dest_path])


def _clone(args, src_dir):
    if os.path.exists(src_dir):
        raise CommandError("Cannot clone into %s, path already exists" % src_dir)

    Dodo.runcmd(
        [
            "git",
            "clone",
            args.git_url,
            os.path.basename(src_dir)
        ] + (["--depth", args.depth] if args.depth else []),
        cwd=os.path.dirname(src_dir)
    )
    if args.branch:
        Dodo.runcmd(
            [
                "git",
                "checkout",
                args.branch
            ],
            cwd=src_dir
        )


def _cookiecutter(src_dir, cookiecutter_url):
    if os.path.exists(src_dir):
        raise CommandError("Cannot clone into %s, path already exists" % src_dir)

    Dodo.runcmd(
        [
            "cookiecutter",
            cookiecutter_url,
            "-o", src_dir
        ]
    )


def _link(src_dir, link_dir):
    if os.path.exists(src_dir):
        raise CommandError("Cannot create a link because %s already exists" % src_dir)
    Dodo.runcmd(["ln", "-s", link_dir, src_dir])


def _create_symlink_to_defaults(project_defaults_dir):
    target_dir = os.path.join(
        args.project_dir,
        "dodo_commands/default_project"
    )
    if os.path.exists(target_dir):
        Dodo.runcmd(["rm", target_dir])
    Dodo.runcmd(["ln", "-s", project_defaults_dir, target_dir])


def _write_src_dir(src_dir):
    config = ConfigIO().load(load_layers=False)
    config['ROOT']['src_dir'] = src_dir
    ConfigIO().save(config)


def _get_full_src_dir(src_dir, src_subdir):
    postfix = (
        os.path.join(src_dir, src_subdir)
        if src_subdir else
        src_dir
    )
    return (
        postfix
        if os.path.isabs(src_dir) else
        os.path.join(args.project_dir, postfix)
    )


if Dodo.is_main(__name__, safe=False):
    args = _args()

    full_src_dir = _get_full_src_dir(args.src_dir, args.src_subdir)
    Dodo.runcmd(['mkdir', '-p', os.path.dirname(full_src_dir)])

    if args.git_url:
        _clone(args, full_src_dir)
    elif args.link_dir:
        _link(full_src_dir, os.path.expanduser(args.link_dir))
    elif args.cookiecutter_url:
        _cookiecutter(full_src_dir, os.path.expanduser(args.cookiecutter_url))

    full_project_defaults_dir = os.path.join(full_src_dir, args.project_defaults_dir)
    if not os.path.exists(full_project_defaults_dir):
        raise CommandError(
            "Default project location %s not found." % full_project_defaults_dir
        )

    _create_symlink_to_defaults(full_project_defaults_dir)
    _copy_defaults(args, full_project_defaults_dir)
    _write_src_dir(
        args.src_dir
        if os.path.isabs(args.src_dir) else
        os.path.join("${/ROOT/project_dir}", args.src_dir)
    )
