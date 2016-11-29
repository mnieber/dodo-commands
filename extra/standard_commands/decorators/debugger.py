class Decorator:  # noqa
    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--use-debugger',
            action='store_true',
            default=False,
            help="Run the command through the debugger"
        )

    def handle(self, decorated, use_debugger, **kwargs):  # noqa
        decorated.opt_use_debugger = use_debugger

    def modify_args(self, decorated, args, cwd):  # noqa
        if not decorated.opt_use_debugger:
            return args, cwd

        new_args = [decorated.get_config('/BUILD/debugger')] + args
        return new_args, cwd
