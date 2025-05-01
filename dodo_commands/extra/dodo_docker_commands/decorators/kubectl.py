"""Decorates command lines with docker arguments."""

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.args_tree import ArgsTreeNode

local = plumbum.local


class Decorator:  # noqa
    @classmethod
    def merged_options(cls, get_config):
        return get_config("/KUBERNETES", {})

    @classmethod
    def kubectl_node(cls, get_config):
        full_container_name = cls.get_full_container_name(get_config)

        if full_container_name:
            return ArgsTreeNode(
                "kubectl",
                args=["kubectl", "exec", "-it", full_container_name, "--"],
            )
        else:
            raise CommandError("No kubernetes container found")

    @classmethod
    def get_full_container_name(cls, get_config):
        options = cls.merged_options(get_config)
        labels = [
            f"-l={key}={value}" for key, value in options.get("labels", {}).items()
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
            )[1:-1].split()[0]
        else:
            full_container_name = None
        return full_container_name

    def add_arguments(self, parser):  # noqa
        pass

    def modify_args(self, command_line_args, args_tree_root_node, cwd):
        kubectl_node = self.kubectl_node(Dodo.get_config)

        kubectl_node.add_child(args_tree_root_node)
        return kubectl_node, local.cwd
