"""Decorates command lines with docker arguments."""
from fnmatch import fnmatch

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.config import merge_into_config
from dodo_commands.framework.decorator_utils import uses_decorator

local = plumbum.local


def _is_tuple(x):
    return hasattr(x, "__len__") and not isinstance(x, type(str()))


class Decorator:  # noqa
    def is_used(self, config, command_name, decorator_name):
        return uses_decorator(config, command_name, decorator_name)

    @classmethod
    def merged_options(cls, get_config, command_name):
        merged = {}
        docker_options = get_config("/KUBERNETES", {})
        for patterns, docker_config in docker_options.items():
            should_merge = False
            for pattern in patterns if _is_tuple(patterns) else [patterns]:
                if pattern.startswith("!"):
                    should_merge = should_merge and not fnmatch(
                        command_name, pattern[1:]
                    )
                else:
                    should_merge = should_merge or fnmatch(command_name, pattern)
            if should_merge:
                merge_into_config(merged, docker_config)
        return merged

    @classmethod
    def kubectl_node(cls, get_config, command_name, cwd):
        merged = cls.merged_options(get_config, command_name)
        container_name = merged.get("container_name")
        kubectl = local["kubectl"]

        if container_name:
            full_container_name = kubectl(
                "get",
                "pods",
                "-l=app.kubernetes.io/name=" + container_name,
                "-o",
                'jsonpath="{.items[0].metadata.name}"',
            )

            return ArgsTreeNode(
                "kubectl",
                args=["kubectl", "exec", "-it", full_container_name[1:-1], "--"],
            )
        else:
            raise CommandError(
                "No kubernetes container name in /KUBERNETES for command %s"
                % command_name
            )

    def add_arguments(self, parser):  # noqa
        pass

    def modify_args(self, command_line_args, args_tree_root_node, cwd):  # override
        kubectl_node = self.kubectl_node(Dodo.get_config, Dodo.command_name, cwd)

        kubectl_node.add_child(args_tree_root_node)
        return kubectl_node, local.cwd
