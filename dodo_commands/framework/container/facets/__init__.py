from dodo_commands.framework import ramda as R

from .command_line import CommandLine  # noqa
from .commands import Commands, init_commands  # noqa
from .config import Config  # noqa
from .layers import Layers, init_layers  # noqa


def i_(facet_class, member, prefix=None, alt_name=None):
    arg_name = alt_name if alt_name else prefix + "_" + member if prefix else member
    return ("in", facet_class, member, arg_name)


def o_(facet_class, member):
    return ("out", facet_class, member)


def map_datas(*args, transform):
    def action(ctr):
        kwargs = {}

        def is_input(arg):
            return arg[0] == "in"

        def do_add_to_kwargs(input_arg):
            _, facet_class, member, arg_name = input_arg
            value = getattr(facet_class.get(ctr), member)
            kwargs[arg_name] = value

        x = args
        # [(in | out, facet_class, member)]
        x = R.filter(is_input)(x)
        # [(in | out, facet_class, member)]
        x = R.for_each(do_add_to_kwargs)(x)
        # [value]
        output_values = transform(**kwargs)

        def is_output(arg):
            return arg[0] == "out"

        def zip_with_output_values(output_args):
            return [
                [output_arg, output_values[output_arg[2]]] for output_arg in output_args
            ]

        def do_store(output_arg, output_value):
            _, facet_class, member = output_arg
            setattr(facet_class.get(ctr), member, output_value)

        x = args
        # [(in | out, facet_class, member)]
        x = R.filter(is_output)(x)
        # [(in | out, facet_class, member)]
        x = zip_with_output_values(x)
        # [((in | out, facet_class, member), output_value)]
        R.for_each(R.ds(do_store))(x)

        return output_values

    return action


def register(*args):
    def decorator(func):
        setattr(func, "action_args", args)
        return func

    return decorator


def run(ctr, action):
    return map_datas(
        *action.action_args,
        transform=action,
    )(ctr)
