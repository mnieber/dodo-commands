from dodo_commands import Dodo
from dodo_commands.framework.args_tree import ArgsTreeNode


class Decorator:  # noqa
    def add_arguments(self, parser):  # noqa
        parser.add_argument(
            "--use-debugger",
            action="store_true",
            default=False,
            help="Run the command through the debugger",
        )

    def modify_args(self, command_line_args, root_node, cwd):  # noqa
        if not getattr(command_line_args, "use_debugger", False):
            return root_node, cwd

        debugger_node = ArgsTreeNode("debugger", args=[Dodo.get("/BUILD/debugger")])
        debugger_node.add_child(root_node)
        return debugger_node, cwd
