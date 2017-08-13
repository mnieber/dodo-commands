from dodo_commands.framework.args_tree import ArgsTreeNode

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

    def modify_args(self, decorated, root_node, cwd):  # noqa
        if not decorated.opt_use_debugger:
            return root_node, cwd

        debugger_node = ArgsTreeNode("debugger", args=[decorated.get_config('/BUILD/debugger')])
        debugger_node.add_child(root_node)
        return debugger_node, cwd
