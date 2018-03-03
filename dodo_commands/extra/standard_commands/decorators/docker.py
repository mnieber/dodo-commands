"""Decorates command lines with docker arguments."""

from plumbum import local
from dodo_commands.framework.args_tree import ArgsTreeNode
from dodo_commands.framework.command_error import CommandError
from fnmatch import fnmatch


def _is_tuple(x):
    return hasattr(x, "__len__") and not isinstance(x, type(str()))


class Decorator:  # noqa
    @classmethod
    def _add_docker_volume_list(cls, docker_config, root_node):
        volume_list = docker_config.get('volume_list', [])
        volume_map = docker_config.get('volume_map', {})
        options = (
            ['--volume=%s:%s' % (x, x) for x in volume_list] +
            ['--volume=%s:%s' % key_val for key_val in volume_map.items()]
        )
        for x in options:
            root_node['volume'].append(x)

    @classmethod
    def _add_docker_publish_list(cls, docker_config, root_node):
        publish_list = docker_config.get('publish_list', [])
        publish_map = docker_config.get('publish_map', {})
        options = (
            ['--publish=%s:%s' % (x, x) for x in publish_list] +
            ['--publish=%s:%s' % key_val for key_val in publish_map.items()]
        )
        for x in options:
            root_node['publish'].append(x)

    @classmethod
    def _add_docker_volumes_from_list(cls, docker_config, root_node):
        volumes_from_list = docker_config.get('volumes_from_list', [])
        options = (
            ['--volumes-from=%s' % x for x in volumes_from_list]
        )
        for x in options:
            root_node['volumes-from'].append(x)

    @classmethod
    def _add_docker_variable_list(cls, docker_config, root_node):
        variable_list = docker_config.get('variable_list', [])
        variable_map = docker_config.get('variable_map', {})
        options = (
            ['--env=%s' % x for x in variable_list] +
            [
                '--env=%s=%s' % key_val
                for key_val in variable_map.items()
            ]
        )
        for x in options:
            root_node['env'].append(x)

    @classmethod
    def _add_linked_container_list(cls, docker_config, root_node):
        options = ['--link=%s' % x for x in docker_config.get('link_list', [])]
        for x in options:
            root_node['link'].append(x)

    @classmethod
    def docker_node(cls, get_config, command_name, cwd, is_interactive):
        key = get_config(
            '/DOCKER/aliases/%s' % command_name, command_name
        )

        docker_node = ArgsTreeNode("docker", args=['docker', 'run'])

        docker_node.add_child(ArgsTreeNode("basic"))
        docker_node.add_child(ArgsTreeNode("name"))
        docker_node.add_child(ArgsTreeNode("link"))
        docker_node.add_child(ArgsTreeNode("publish"))
        docker_node.add_child(ArgsTreeNode("volume", is_horizontal=False))
        docker_node.add_child(ArgsTreeNode("volumes-from"))
        docker_node.add_child(ArgsTreeNode("env", is_horizontal=False))
        docker_node.add_child(ArgsTreeNode("other"))
        docker_node.add_child(ArgsTreeNode("workdir"))
        docker_node.add_child(ArgsTreeNode("image"))

        name = command_name
        image = None
        rm = True
        for patterns, docker_config in get_config('/DOCKER/options', {}).items():
            for pattern in (patterns if _is_tuple(patterns) else [patterns]):
                if fnmatch(key, pattern):
                    image = docker_config.get('image', image)
                    rm = docker_config.get('rm', rm)
                    name = docker_config.get('name', name)

                    cls._add_docker_variable_list(docker_config, docker_node)
                    cls._add_docker_volume_list(docker_config, docker_node)
                    cls._add_docker_publish_list(docker_config, docker_node)
                    cls._add_docker_volumes_from_list(docker_config, docker_node)
                    cls._add_linked_container_list(docker_config, docker_node)
                    for x in docker_config.get('extra_options', []):
                        docker_node['other'].append(x)

        for key_val in get_config('/ENVIRONMENT/variable_map', {}).items():
            docker_node['env'].append("--env=%s=%s" % key_val)
        if rm:
            docker_node['basic'].append('--rm')
        docker_node["name"].append("--name=%s" % name)
        if is_interactive:
            docker_node['basic'].append('--interactive')
            docker_node['basic'].append('--tty')
        if cwd:
            docker_node['workdir'].append('--workdir=' + cwd)

        if not image:
            raise CommandError(
                "No docker image found in /DOCKER/options for command %s"
                % command_name
            )
        docker_node["image"].append(image)

        return docker_node, image, name

    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help="Run docker calls without -i and -t"
        )
        parser.add_argument(
            '--kill-existing',
            action='store_true',
            help="Kill and remove existing docker container with the same name"
        )

    def handle(
        self, decorated, non_interactive, kill_existing, **kwargs
    ):  # noqa
        decorated.opt_non_interactive = non_interactive
        decorated.opt_kill_existing = kill_existing

    def _kill_existing_container(self, name):
        docker = local['docker']
        live_containers = docker(
            "ps",
            "--format={{.Names}}",
            "--filter=name=^/%s$" % name
        )
        if len(live_containers):
            docker("stop", name)

        exited_containers = docker(
            "ps",
            "-a",
            "--format={{.Names}}",
            "--filter=name=^/%s$" % name
        )
        if len(exited_containers):
            docker("rm", name)

    def modify_args(self, decorated, root_node, cwd):  # noqa
        docker_node, _, docker_name = self.docker_node(
            decorated.get_config,
            decorated.name,
            cwd,
            not decorated.opt_non_interactive
        )

        if decorated.opt_kill_existing:
            self._kill_existing_container(docker_name)

        docker_node.add_child(root_node)
        return docker_node, local.cwd
