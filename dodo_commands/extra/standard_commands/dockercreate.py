# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from dodo_commands.framework.config import ConfigIO
from plumbum.cmd import docker

class Command(DodoCommand):  # noqa
    help = ""
    decorators = []

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            'container_type',
            choices=self.get_config('/DOCKER/container_types', {}).keys()
        )
        parser.add_argument('name')

    def handle_imp(self, container_type, name, **kwargs):  # noqa
        existing = docker("ps", "-a", "--quiet", "--filter", "name=" + name)
        if not existing:
            args = [
                "docker",
                "create",
                "--name", name,
            ]

            for path in self.get_config(
                "/DOCKER/container_types/%s/dirs" % container_type
            ):
                args.extend(["-v", path])

            args.append(self.get_config(
                "/DOCKER/container_types/%s/image" % container_type
            ))
            self.runcmd(args)

        config = ConfigIO().load(load_layers=False)
        config['DOCKER'].setdefault('containers', {})[container_type] = name
        ConfigIO().save(config)
