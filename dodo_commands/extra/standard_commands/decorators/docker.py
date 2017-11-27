"""Decorates command lines with docker arguments."""

from plumbum import local
from dodo_commands.framework import CommandError
from dodo_commands.framework.args_tree import ArgsTreeNode
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
    def get_image_name(cls, get_config, name):
        result = get_config('/DOCKER/options/%s/image' % name, '')
        if result:
            return result

        for patterns, docker_config in get_config('/DOCKER/options', {}).items():
            for pattern in (patterns if _is_tuple(patterns) else [patterns]):
                if name and fnmatch(name, pattern):
                    result = docker_config.get('image', None)
                    if result:
                        return result

        raise CommandError("Could not find docker image for %s" % name)

    @classmethod
    def _add_config_docker_options(cls, get_config, name, root_node):
        for key_val in get_config('/ENVIRONMENT/variable_map', {}).items():
            root_node['env'].append("--env=%s=%s" % key_val)

        for patterns, docker_config in get_config('/DOCKER/options', {}).items():
            for pattern in (patterns if _is_tuple(patterns) else [patterns]):
                if name and fnmatch(name, pattern):
                    cls._add_docker_variable_list(docker_config, root_node)
                    cls._add_docker_volume_list(docker_config, root_node)
                    cls._add_docker_volumes_from_list(docker_config, root_node)
                    cls._add_linked_container_list(docker_config, root_node)
                    for x in docker_config.get('extra_options', []):
                        root_node['other'].append(x)

    def add_arguments(self, decorated, parser):  # noqa
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help="Run docker calls without -i and -t"
        )

    def handle(self, decorated, non_interactive, **kwargs):  # noqa
        decorated.opt_non_interactive = non_interactive

    @classmethod
    def _add_options(cls, decorated, cwd, root_node):
        name = None

        if not hasattr(decorated, 'docker_rm') or decorated.docker_rm:
            root_node['basic'].append('--rm')
        if not decorated.opt_non_interactive:
            root_node['basic'].append('--interactive')
            root_node['basic'].append('--tty')
        if cwd:
            root_node['workdir'].append('--workdir=' + cwd)
        if hasattr(decorated, "docker_options"):
            for p in decorated.docker_options:
                try:
                    key, val = p
                    if key == "name":
                        name = val
                    child_name = key if root_node.has_child(key) else "other"
                    root_node[child_name].append(cls._to_opt(key, val))
                except:
                    raise CommandError(
                        "Elements of docker_options must be tuples of type (key, val)"
                    )

        return name

    @classmethod
    def _to_opt(cls, key, val):
        return '--%s' % key if val is None else '--%s=%s' % (key, val)

    @classmethod
    def _container_name(cls, options):
        for key, val in options:
            if key == 'name':
                return val
        return ""

    def modify_args(self, decorated, root_node, cwd):  # noqa
        docker_node = ArgsTreeNode("docker", args=['docker', 'run'])
        docker_node.add_child(ArgsTreeNode("basic"))
        docker_node.add_child(ArgsTreeNode("name"))
        docker_node.add_child(ArgsTreeNode("link"))
        docker_node.add_child(ArgsTreeNode("volume", is_horizontal=False))
        docker_node.add_child(ArgsTreeNode("volumes-from"))
        docker_node.add_child(ArgsTreeNode("env", is_horizontal=False))
        docker_node.add_child(ArgsTreeNode("other"))
        docker_node.add_child(ArgsTreeNode("workdir"))

        name = self._add_options(decorated, cwd, docker_node)
        self._add_config_docker_options(decorated.get_config, name, docker_node)

        docker_node.add_child(
            ArgsTreeNode("image", args=[self.get_image_name(decorated.get_config, name)])
        )
        docker_node.add_child(root_node)

        return docker_node, local.cwd
