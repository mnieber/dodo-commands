from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError
from dodo_commands.framework.config import (get_global_config,
                                            global_config_filename, ConfigIO)
from six.moves import configparser
import os


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.editor = get_global_config().get("settings", "config_editor")
    args.res_dir = Dodo.get_config('/ROOT/res_dir')
    return args


if Dodo.is_main(__name__, safe=True):
    try:
        args = _args()
    except configparser.NoOptionError as e:
        raise CommandError("{error}. Please check {filename}".format(
            error=str(e), filename=global_config_filename()))

    yaml_filenames = ([os.path.join(args.res_dir, 'config.yaml')] +
                      ConfigIO().get_layers(Dodo.config))

    yaml_filenames.append(global_config_filename())
    Dodo.runcmd([args.editor] + yaml_filenames, cwd='.')
