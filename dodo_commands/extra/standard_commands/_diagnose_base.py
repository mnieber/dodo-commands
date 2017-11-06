import plumbum


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

    def _image(self, key):
        image = self.get_config(key, None)
        if not image:
            self.prnt_error("Missing docker image configuration value: %s" % key)
        return image

    def _print_yes_no(self, flag, yes_msg, no_msg, key):
        if flag:
            self.prnt(" yes")
            if yes_msg:
                self.prnt(yes_msg % dict(key=key))
        else:
            self.prnt(" no")
            if no_msg:
                self.prnt_next(no_msg % dict(key=key))

    def check_docker_image(self, key, yes_msg, no_msg):
        docker = self._docker()
        image = self._image(key)

        self.prnt(
            "Checking if docker image ##${%s}## is found locally:" % key,
            new_line=False
        )

        docker_image_exists = docker("images", "-q", image)
        self._print_yes_no(docker_image_exists, yes_msg, no_msg, key)

    def check_docker_container(self, key, yes_msg, no_msg):
        docker = self._docker()
        image = self._image(key)

        self.prnt(
            "Checking if docker container ##${%s}## is found locally:" % key,
            new_line=False
        )

        container_exists = image in docker("ps", "-a", "--filter=name=%s" % image)
        self._print_yes_no(container_exists, yes_msg, no_msg, key)
