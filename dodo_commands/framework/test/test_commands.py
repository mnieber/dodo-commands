"""Tests for all standard commands."""
import os
import shutil
import sys

from dodo_commands.dependencies import yaml_round_trip_dump, yaml_round_trip_load

docker_on_yaml = """
DOCKER_OPTIONS:
  "*":
    image: dodo_tutorial:1604

DOCKER_IMAGES:
  base:
    image: dodo_tutorial:1604

ROOT:
  command_path:
  - ${/ROOT/project_dir}/src/part4/after/src/commands
"""


class TestConfigIO:  # noqa
    @classmethod
    def _load_config(cls, config_filename):
        with open(config_filename) as f:
            return yaml_round_trip_load(f.read())

    @classmethod
    def _write_config(cls, config, config_filename):
        with open(config_filename, "w") as f:
            f.write(yaml_round_trip_dump(config))

    @classmethod
    def _set_config_version(cls, config_filename, version):
        config = cls._load_config(config_filename)
        config["ROOT"]["version"] = version
        cls._write_config(config, config_filename)

    @classmethod
    def _set_required_dodo_version(cls, config_filename, version):
        config = cls._load_config(config_filename)
        config["ROOT"]["required_dodo_commands_version"] = version
        cls._write_config(config, config_filename)

    @classmethod
    def _clear_layers(cls, config_filename):
        config = cls._load_config(config_filename)
        config["LAYERS"] = []
        cls._write_config(config, config_filename)

    def test_commands(self):  # noqa
        from dodo_commands.dependencies.get import plumbum

        local = plumbum.local

        dodo_test_dir = os.path.expanduser("~/projects/dodo_test")
        dodo_bin_dir = os.path.expanduser("~/.dodo_commands/bin")
        dodo_test_env_dir = os.path.expanduser("~/.dodo_commands/envs/dodo_test")
        config_dir = os.path.join(dodo_test_dir, ".dodo_commands")
        config_filename = os.path.join(config_dir, "config.yaml")
        skip_install = False

        if not skip_install:
            if os.path.exists(dodo_test_dir):
                shutil.rmtree(dodo_test_dir)
            if os.path.exists(dodo_test_env_dir):
                shutil.rmtree(dodo_test_env_dir)

            from dodo_commands.dodo import main

            sys.argv = ["dodo", "env", "--create", "--create-python-env", "dodo_test"]
            main()

        dodo = local[os.path.join(dodo_bin_dir, "dodo-dodo_test")]
        if not skip_install:
            dodo(
                "bootstrap",
                "src",
                "extra/dodo_commands/config",
                "--force",
                "--git-url",
                "https://github.com/mnieber/dodo_commands_tutorial.git",
            )

            # create shared config file
            extra_dir = os.path.join(dodo_test_dir, "extra")
            os.makedirs(extra_dir)

            config = self._load_config(config_filename)
            self._write_config(config, os.path.join(extra_dir, "config.yaml"))
            config["ROOT"]["shared_config_dir"] = "${/ROOT/project_dir}/extra"
            self._write_config(config, config_filename)

        # dodo which
        assert "dodo_test" == dodo("which")[:-1]
        assert dodo_test_dir == dodo("which", "--project-dir")[:-1]
        assert config_dir == dodo("which", "--config-dir")[:-1]
        assert config_filename == dodo("which", "--config")[:-1]
        assert "confirm, debugger, docker, pause" == dodo("which", "--decorators")[:-1]

        # dodo cd
        assert "cd " + dodo_test_dir == dodo("which --cd --project-dir")[:-1]

        # dodo check-version --config
        self._set_config_version(config_filename, "0.1.0")
        assert (
            "Configuration needs update (0.1.0 < 1.0.0)"
            in dodo("check-version", "--config")[:-1]
        )
        self._set_config_version(config_filename, "1.0.0")

        # dodo check-version --dodo
        self._set_required_dodo_version(config_filename, "10000.0.0")
        assert (
            "The dodo_commands package needs to be upgraded"
            in dodo("check-version", "--dodo")[:-1]
        )
        self._set_required_dodo_version(config_filename, dodo("--version")[:-1])
        assert "" == dodo("check-version", "--dodo")[:-1]

        # dodo diff
        result = dodo("diff", ".", "--echo").replace("\n", "")
        diff_tool = result.split()[0]
        assert "%s %s/extra %s/." % (diff_tool, dodo_test_dir, config_dir) == result

        # dodo docker
        with open(os.path.join(config_dir, "docker.on.yaml"), "w") as ofs:
            ofs.write(docker_on_yaml)

        dodo("layer", "docker", "on")
        result = (
            dodo("docker", "*", "--name", "foo", "--echo")
            .replace("\n", "")
            .replace("  \\", "")
            .replace("  ", " ")
        )
        assert (
            "docker run --name=foo --interactive --tty --rm --workdir=/ dodo_tutorial:1604 sh"
            == result
        )

        # dodo docker-build
        result = (
            dodo("docker-build", "--echo", "base").replace("\n", "").replace("  \\", "")
        )
        assert "docker build -t dodo_tutorial:1604 -f Dockerfile ." == result

        # dodo print-config
        assert "image: dodo_tutorial:1604" in dodo("print-config")

        # dodo drop-in
        tutorial_commands_dir = os.path.join(
            dodo_test_dir, "src/part4/after/src/commands"
        )
        drop_in_dir = os.path.join(tutorial_commands_dir, "drop-in")
        os.mkdir(drop_in_dir)
        with open(os.path.join(drop_in_dir, "bar.txt"), "w") as ofs:
            ofs.write("bar")
        target_bar_path = os.path.join(config_dir, "drops", "commands", "bar.txt")
        assert not os.path.exists(target_bar_path)
        dodo("drop-in", "commands")
        assert os.path.exists(target_bar_path)
