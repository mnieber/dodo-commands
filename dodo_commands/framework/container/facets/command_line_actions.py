import argparse
import sys

from dodo_commands.framework import ramda as R
from dodo_commands.framework.container.facets import CommandLine, i_, map_datas, o_
from dodo_commands.framework.container.utils import rearrange_double_dash


def register(*args):
    def decorator(func):
        setattr(func, "action_args", args)
        return func

    return decorator


def run(ctr, action):
    return map_datas(*action.action_args, transform=action,)(ctr)


@register(
    i_(CommandLine, "is_running_directly_from_script"),
    i_(CommandLine, "is_help"),
    o_(CommandLine, "given_layer_paths"),
    o_(CommandLine, "is_trace"),
    o_(CommandLine, "input_args"),
)
def parse_sys_argv(is_running_directly_from_script, is_help):
    parser = argparse.ArgumentParser()
    parser.add_argument("-L", "--layer", action="append")
    parser.add_argument("--trace", action="store_true")

    known_args, args = R.pipe(
        R.always(rearrange_double_dash(sys.argv)),
        R.when(R.always(is_running_directly_from_script), R.prepend(sys.executable)),
        R.when(R.always(is_help), R.filter(lambda x: x != "--help")),
        parser.parse_known_args,
    )(None)

    return dict(
        given_layer_paths=known_args.layer or [],
        is_trace=known_args.trace,
        input_args=args,
    )
