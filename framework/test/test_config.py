"""Tests for config.py."""

import os
import pytest
import yaml
from ..config import ConfigIO


class TestConfigIO:  # noqa
    simple_config = {
        'ROOT': {
            'layer_dir': 'layers',
            'layers': ['mylayer.yml'],
            'command_path': [
                'foo',
                'bar'
            ],
            'foo': {
                'bar': 'foobar',
                'one': 'two'
            },
            'one': 1
        }
    }

    layer = {
        'ROOT': {
            'command_path': [
                'foobar',
            ],
            'foo': {
                'bar': 'barfoo',
                'three': 4
            },
            'one': 1.1
        }
    }

    @pytest.fixture
    def create_config(self, tmpdir):
        """Create a config file in the tmpdir."""
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(self.simple_config)

    @pytest.fixture
    def create_layer(self, tmpdir):
        """Create a config layer file in the tmpdir."""
        layer_dir = os.path.join(str(tmpdir), "layers")
        os.mkdir(layer_dir)
        layer_filename = os.path.join(layer_dir, "mylayer.yml")
        with open(layer_filename, "w") as f:
            f.write(
                yaml.dump(self.layer, default_flow_style=False, indent=4)
            )

    def test_save(self, tmpdir):  # noqa
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(self.simple_config)
        config = configIO.load(load_layers=False)
        assert self.simple_config == config

    @pytest.mark.usefixtures("create_config", "create_layer")
    def test_layers(self, tmpdir):  # noqa
        configIO = ConfigIO(str(tmpdir))  # noqa
        full_config = configIO.load()

        assert full_config['ROOT']['command_path'] == ['foo', 'bar', 'foobar']
        assert full_config['ROOT']['foo'] == {
            'bar': 'barfoo',
            'one': 'two',
            'three': 4,
        }
        assert full_config['ROOT']['one'] == 1.1
