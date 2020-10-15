"""Tests for config.py."""

import os

from dodo_commands.dependencies import yaml_round_trip_dump

import pytest

from ..config import load_config
from ..config_io import ConfigIO


class TestConfigIO:  # noqa
    @pytest.fixture
    def simple_config(self, tmpdir):
        foo_dir = os.path.join(str(tmpdir), "foo")
        return {
            "LAYERS": ["mylayer.yml"],
            "ROOT": {
                "command_path": [os.path.join(foo_dir, "bar")],
                "foo": {"bar": "foobar", "one": "two"},
                "one": 1,
            },
        }

    @pytest.fixture
    def layer(self, tmpdir):
        foo_dir = os.path.join(str(tmpdir), "foo")
        return {
            "ROOT": {
                "command_path": [
                    os.path.join(foo_dir, "foobar"),
                ],
                "foo": {"bar": "barfoo", "three": 4},
                "one": 1.1,
            }
        }

    @pytest.fixture
    def create_config(self, tmpdir, simple_config):
        """Create a config file in the tmpdir."""
        config_io = ConfigIO(str(tmpdir))  # noqa
        config_io.save(simple_config)

    @pytest.fixture
    def create_layer(self, tmpdir, layer):
        """Create a config layer file in the tmpdir."""
        layer_filename = os.path.join(str(tmpdir), "mylayer.yml")
        with open(layer_filename, "w") as f:
            f.write(yaml_round_trip_dump(layer))

    def test_save(self, tmpdir, simple_config):  # noqa
        config_io = ConfigIO(str(tmpdir))  # noqa
        config_io.save(simple_config)
        config = config_io.load()
        assert simple_config == config

    @pytest.mark.usefixtures("create_config", "create_layer")
    def test_layers(self, tmpdir):  # noqa
        foo_dir = os.path.join(str(tmpdir), "foo")
        config_io = ConfigIO(str(tmpdir))  # noqa
        full_config = load_config(["config.yaml", "mylayer.yml"], config_io=config_io)

        assert full_config["ROOT"]["command_path"] == [
            os.path.join(foo_dir, "bar"),
            os.path.join(foo_dir, "foobar"),
        ]
        assert full_config["ROOT"]["foo"] == {
            "bar": "barfoo",
            "one": "two",
            "three": 4,
        }
        assert full_config["ROOT"]["one"] == 1.1
