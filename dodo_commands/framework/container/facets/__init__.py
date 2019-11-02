from .layers import Layers, init_layers  # noqa
from .command_line import CommandLine, init_command_line  # noqa
from .config import Config  # noqa
from .commands import Commands, init_commands  # noqa
from dodo_commands.framework.funcy import (ds, for_each, keep_if)


def i_(facet_class, member, prefix=None, alt_name=None):
    arg_name = (alt_name if alt_name else prefix + '_' +
                member if prefix else member)
    return ('in', facet_class, member, arg_name)


def o_(facet_class, member):
    return ('out', facet_class, member)


def map_datas(*args, transform=None):
    def action(ctr):
        kwargs = {}

        def is_input(arg):
            return arg[0] == 'in'

        def do_add_to_kwargs(input_arg):
            _, facet_class, member, arg_name = input_arg
            value = getattr(facet_class.get(ctr), member)
            kwargs[arg_name] = value

        x = args
        # [(in | out, facet_class, member)]
        x = keep_if(is_input)(x)
        # [(in | out, facet_class, member)]
        x = for_each(do_add_to_kwargs)(x)
        # [value]
        output_values = transform(**kwargs)

        def is_output(arg):
            return arg[0] == 'out'

        def zip_with_output_values(output_args):
            assert len(output_args) == len(output_values)
            return zip(output_args, output_values)

        def do_store(output_arg, output_value):
            _, facet_class, member = output_arg
            setattr(facet_class.get(ctr), member, output_value)

        x = args
        # [(in | out, facet_class, member)]
        x = keep_if(is_output)(x)
        # [(in | out, facet_class, member)]
        x = zip_with_output_values(x)
        # [((in | out, facet_class, member), output_value)]
        for_each(ds(do_store))(x)

    return action
