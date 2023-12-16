"""Decorates command lines with docker arguments."""

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.args_tree import ArgsTreeNode

local = plumbum.local


def _is_tuple(x):
    return hasattr(x, "__len__") and not isinstance(x, type(str()))


class Decorator:  # noqa
    @classmethod
    def merged_options(cls, get_config, command_name):
        return get_config("/KUBERNETES", {})

    @classmethod
    def kubectl_node(cls, get_config, command_name, cwd):
        merged = cls.merged_options(get_config, command_name)
        labels = [
            f"-l={key}={value}" for key, value in merged.get("labels", {}).items()
        ]
        kubectl = local["kubectl"]

        if labels:
            full_container_name = kubectl(
                "get",
                "pods",
                *labels,
                "-o",
                'jsonpath="{.items[*].metadata.name}"',
                "--field-selector",
                "status.phase=Running",
            )[1:-1]

            return ArgsTreeNode(
                "kubectl",
                args=["kubectl", "exec", "-it", full_container_name, "--"],
            )
        else:
            raise CommandError(
                "No kubernetes container name in /KUBERNETES for command %s"
                % command_name
            )

    def add_arguments(self, parser):  # noqa
        pass

    def modify_args(
        self, command_line_args, args_tree_root_node, cwd, env_variable_map
    ):
        kubectl_node = self.kubectl_node(Dodo.get_config, Dodo.command_name, cwd)

        kubectl_node.add_child(args_tree_root_node)
        return kubectl_node, local.cwd
