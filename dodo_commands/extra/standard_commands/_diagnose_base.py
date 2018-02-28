import plumbum
from dodo_commands.extra.standard_commands.decorators.docker import Decorator as DockerDecorator


class DiagnoseBase:
    def __init__(self, get_config, prnt, prnt_next, prnt_error):
        self.prnt = prnt
        self.prnt_next = prnt_next
        self.prnt_error = prnt_error
        self.get_config = get_config

    def _docker(self):
        try:
            return plumbum.local['docker']
        except plumbum.commands.processes.CommandNotFound:
            self.prnt_error("Docker is not installed")

    def _image(self, key_or_name):
        image = self.get_config(key_or_name, None)
        if not image:
            _, image, _ = DockerDecorator.docker_node(
                self.get_config, key_or_name, "", False
            )

        if not image:
            self.prnt_error("Missing docker image configuration value for docker with name: %s" % key_or_name)
        return image

    def _print_yes_no(self, flag, yes_msg, no_msg, image):
        if flag:
            self.prnt(" yes")
            if yes_msg:
                self.prnt(yes_msg % dict(image=image))
        else:
            self.prnt(" no")
            if no_msg:
                self.prnt_next(no_msg % dict(image=image))

    def check_docker_image(self, key_or_name, yes_msg, no_msg):
        docker = self._docker()
        image = self._image(key_or_name)

        self.prnt(
            "Checking if docker image for %s (%s) is found locally:"
            % (key_or_name, image),
            new_line=False
        )

        docker_image_exists = docker("images", "-q", image)
        self._print_yes_no(docker_image_exists, yes_msg, no_msg, image)

    def check_docker_container(self, key, yes_msg, no_msg):
        docker = self._docker()
        image = self._image(key)

        self.prnt(
            "Checking if docker container ##${%s}## is found locally:" % key,
            new_line=False
        )

        container_exists = image in docker("ps", "-a", "--filter=name=%s" % image)
        self._print_yes_no(container_exists, yes_msg, no_msg, image)
