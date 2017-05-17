"""Tests for config.py."""

import os
import pytest
import ruamel.yaml
from ..config import ConfigIO


class TestConfigIO:  # noqa
    @pytest.fixture
    def simple_config(self, tmpdir):
        foo_dir = os.path.join(str(tmpdir), 'foo')
        return {
            'ROOT': {
                'layer_dir': 'layers',
                'layers': ['mylayer.yml'],
                'command_path': [
                    [foo_dir, 'bar']
                ],
                'foo': {
                    'bar': 'foobar',
                    'one': 'two'
                },
                'one': 1
            }
        }

    @pytest.fixture
    def layer(self, tmpdir):
        foo_dir = os.path.join(str(tmpdir), 'foo')
        return {
            'ROOT': {
                'command_path': [
                    [foo_dir, 'foobar'],
                ],
                'foo': {
                    'bar': 'barfoo',
                    'three': 4
                },
                'one': 1.1
            }
        }

    @pytest.fixture
    def create_config(self, tmpdir, simple_config):
        """Create a config file in the tmpdir."""
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(simple_config)

    @pytest.fixture
    def create_layer(self, tmpdir, layer):
        """Create a config layer file in the tmpdir."""
        layer_dir = os.path.join(str(tmpdir), "layers")
        os.mkdir(layer_dir)
        layer_filename = os.path.join(layer_dir, "mylayer.yml")
        with open(layer_filename, "w") as f:
            f.write(ruamel.yaml.round_trip_dump(layer))

    def test_save(self, tmpdir, simple_config):  # noqa
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(simple_config)
        config = configIO.load(load_layers=False)
        assert simple_config == config

    @pytest.mark.usefixtures("create_config", "create_layer")
    def test_layers(self, tmpdir):  # noqa
        foo_dir = os.path.join(str(tmpdir), 'foo')
        configIO = ConfigIO(str(tmpdir))  # noqa
        full_config = configIO.load()

        assert full_config['ROOT']['command_path'] == [
            [foo_dir, 'bar'],
            [foo_dir, 'foobar'],
        ]
        assert full_config['ROOT']['foo'] == {
            'bar': 'barfoo',
            'one': 'two',
            'three': 4,
        }
        assert full_config['ROOT']['one'] == 1.1
