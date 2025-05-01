"""Decorates command lines with docker arguments."""

import os

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.args_tree import ArgsTreeNode

local = plumbum.local


def invert_path(path):
    def _len(path):
        return len(path.split(os.sep))

    options = Decorator.merged_options(Dodo.get, Dodo.command_name)
    inverse_volume_map = options.get("inverse_volume_map", {})
    best_common_path = ""
    best_host_path = ""

    for container_path, host_path in inverse_volume_map.items():
        common_path = os.path.commonpath([path, container_path])
        if _len(common_path) > _len(best_common_path):
            best_common_path = common_path
            best_host_path = os.path.join(host_path, os.path.relpath(path, common_path))

    return best_host_path


# Resp: reads docker related settings from the docker_config and uses
# them to modify the current args_tree_root_node.


class Decorator:  # noqa
    @classmethod
    def _add_docker_volume_list(cls, docker_config, root_node):
        volume_list = docker_config.get("volume_list", [])
        volume_map = docker_config.get("volume_map", {})

        volume_map_strict = docker_config.get("volume_map_strict", {})
        for key, val in volume_map_strict.items():
            if not os.path.exists(key):
                raise CommandError("Path in volume_map_strict not found: %s" % key)
            volume_map[key] = val

        options = ["--volume=%s:%s" % (x, x) for x in volume_list] + [
            "--volume=%s:%s" % key_val for key_val in volume_map.items()
        ]
        for x in options:
            root_node["volume"].append(x)

    @classmethod
    def _add_docker_publish_list(cls, docker_config, root_node):
        publish_list = docker_config.get("publish_list", [])
        publish_map = docker_config.get("publish_map", {})
        options = ["--publish=%s:%s" % (x, x) for x in publish_list] + [
            "--publish=%s:%s" % key_val for key_val in publish_map.items()
        ]
        for x in options:
            root_node["publish"].append(x)

    @classmethod
    def _add_docker_volumes_from_list(cls, docker_config, root_node):
        volumes_from_list = docker_config.get("volumes_from_list", [])
        options = ["--volumes-from=%s" % x for x in volumes_from_list]
        for x in options:
            root_node["volumes-from"].append(x)

    @classmethod
    def _add_docker_variable_list(cls, docker_config, root_node):
        variable_list = docker_config.get("variable_list", [])
        variable_map = docker_config.get("variable_map", {})
        options = ["--env=%s" % x for x in variable_list] + [
            "--env=%s=%s" % key_val for key_val in variable_map.items()
        ]
        for x in options:
            root_node["env"].append(x)

    @classmethod
    def _add_linked_container_list(cls, docker_config, root_node):
        options = ["--link=%s" % x for x in docker_config.get("link_list", [])]
        for x in options:
            root_node["link"].append(x)

    @classmethod
    def _add_interactive(cls, docker_config, docker_node):
        if docker_config.get("is_interactive", True):
            docker_node["basic"].append("--interactive")
            docker_node["basic"].append("--tty")

    @classmethod
    def _add_workdir(cls, docker_config, docker_node, cwd):
        if cwd and not ("workdir" in docker_config and not docker_config["workdir"]):
            docker_node["workdir"].append("--workdir=" + cwd)
        elif docker_config.get("workdir", ""):
            docker_node["workdir"].append("--workdir=" + docker_config.get("workdir"))

    @classmethod
    def _add_user(cls, docker_config, docker_node):
        if docker_config.get("user", False):
            docker_node["basic"].extend(["--user", docker_config["user"]])

    @classmethod
    def _add_environment_vars(cls, get_config, docker_config, docker_node):
        for key_val in get_config("/ENVIRONMENT/variable_map", {}).items():
            docker_node["env"].append("--env=%s=%s" % key_val)

    @classmethod
    def _add_extra_options(cls, docker_config, docker_node):
        for x in docker_config.get("extra_options", []):
            docker_node["other"].append(x)

    @classmethod
    def merged_options(cls, get_config, command_name):
        return get_config("/DOCKER", {})

    @classmethod
    def docker_node(cls, get_config, command_name, cwd):
        merged = cls.merged_options(get_config, command_name)

        image, container = merged.get("image"), merged.get("container")

        if image:
            docker_node = ArgsTreeNode("docker", args=["docker", "run"])
            docker_node.add_child(ArgsTreeNode("name"))
            docker_node.add_child(ArgsTreeNode("basic"))
            docker_node.add_child(ArgsTreeNode("link"))
            docker_node.add_child(ArgsTreeNode("publish"))
            docker_node.add_child(ArgsTreeNode("volume", is_horizontal=False))
            docker_node.add_child(ArgsTreeNode("volumes-from"))
            docker_node.add_child(ArgsTreeNode("env", is_horizontal=False))
            docker_node.add_child(ArgsTreeNode("other"))
            docker_node.add_child(ArgsTreeNode("workdir"))
            docker_node.add_child(ArgsTreeNode("image"))

            cls._add_linked_container_list(merged, docker_node)
            cls._add_docker_publish_list(merged, docker_node)
            cls._add_docker_volume_list(merged, docker_node)
            cls._add_docker_volumes_from_list(merged, docker_node)
            cls._add_docker_variable_list(merged, docker_node)
            cls._add_workdir(merged, docker_node, cwd)
            cls._add_interactive(merged, docker_node)
            cls._add_user(merged, docker_node)
            cls._add_environment_vars(get_config, merged, docker_node)
            cls._add_extra_options(merged, docker_node)

            if merged.get("rm", True):
                docker_node["basic"].append("--rm")

            if merged.get("is_daemon", False):
                docker_node["basic"].append("-d")

            name = merged.get("name", command_name)
            if name:
                docker_node["name"].append("--name=%s" % name)

            docker_node["image"].append(image)
        elif container:
            docker_node = ArgsTreeNode("docker", args=["docker", "exec"])
            docker_node.add_child(ArgsTreeNode("basic"))
            docker_node.add_child(ArgsTreeNode("env", is_horizontal=False))
            docker_node.add_child(ArgsTreeNode("other"))
            docker_node.add_child(ArgsTreeNode("workdir"))
            docker_node.add_child(ArgsTreeNode("container"))

            cls._add_interactive(merged, docker_node)
            cls._add_docker_variable_list(merged, docker_node)
            cls._add_workdir(merged, docker_node, cwd)
            cls._add_user(merged, docker_node)
            cls._add_environment_vars(get_config, merged, docker_node)
            cls._add_extra_options(merged, docker_node)
            docker_node["container"].append(container)
        else:
            raise CommandError(
                "No docker image or container found in /DOCKER for command %s"
                % command_name
            )

        return docker_node, image

    def add_arguments(self, parser):  # noqa
        pass

    def modify_args(self, command_line_args, args_tree_root_node, cwd):
        docker_node, _ = self.docker_node(Dodo.get_config, Dodo.command_name, cwd)

        docker_node.add_child(args_tree_root_node)
        return docker_node, local.cwd
