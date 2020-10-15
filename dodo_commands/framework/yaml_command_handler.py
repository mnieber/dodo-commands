import os
import shlex
from argparse import ArgumentParser

from dodo_commands.dependencies import yaml_round_trip_load
from dodo_commands.framework.command_map import CommandMapItem
from dodo_commands.framework.config import Key, expand_keys
from dodo_commands.framework.singleton import Dodo
from dodo_commands.framework.util import chop


class YamlCommandMapItem(CommandMapItem):
    def __init__(self, group, filename):
        super(YamlCommandMapItem, self).__init__(group, filename, "yaml")


class YamlCommandHandler:
    def add_commands_to_map(self, command_dirs, file_map, command_map):
        for command_dir, files in file_map.items():
            for file in files:
                command_name, ext = os.path.splitext(os.path.basename(file))
                prefix = "dodo."
                if ext == ".yaml" and command_name.startswith(prefix):
                    command_name = command_name[len(prefix) :]
                    with open(file) as ifs:
                        data = yaml_round_trip_load(ifs.read())
                        for command_name in data.keys():
                            command_map[command_name] = YamlCommandMapItem(
                                group=os.path.basename(command_dir), filename=file
                            )

    def _expand(self, x):
        return os.path.expanduser(os.path.expandvars(expand_keys(Dodo.get(), x)))

    def execute(self, command_map_item, command_name):
        with open(command_map_item.filename) as ifs:
            data = yaml_round_trip_load(ifs.read())

        description = None
        for key, val in data[command_name].items():
            if key == "_description":
                description = val

        parser = ArgumentParser(description=description)

        for key, val in data[command_name].items():
            if key == "_args":
                for arg in val:
                    default_val = None
                    if arg.startswith("--") and "=" in arg:
                        arg, default_val = arg.split("=")
                        parser.add_argument(
                            arg, nargs="?", const=self._expand(default_val)
                        )
                    else:
                        parser.add_argument(
                            arg,
                        )

        args = Dodo.parse_args(parser)
        Dodo.get()["_ARGS"] = args.__dict__

        for name, cmd in data[command_name].items():
            if name.startswith("_"):
                continue

            args = cmd["args"]
            if isinstance(args, str):
                args = shlex.split(args)

            try:
                cwd = self._expand(cmd.get("cwd"))
            except:  # noqa
                cwd = None

            store_xpath = cmd.get("store", "")
            res = Dodo.run(
                [self._expand(x) for x in args], cwd=cwd, capture=bool(store_xpath)
            )
            if store_xpath:
                key = Key(Dodo.get(), store_xpath)
                key.set(chop(res))
