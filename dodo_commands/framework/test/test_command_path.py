"""Tests for config.py."""

import pytest
import os
from ..config import ConfigIO, CommandPath


class TestCommandPaths:  # noqa
    @pytest.fixture
    def simple_config(self, tmpdir):
        foo_dir = os.path.join(str(tmpdir), 'foo')
        return {
            'ROOT': {
                'command_path': [os.path.join(foo_dir, '*'), ],
                'command_path_exclude': [os.path.join(foo_dir, 'bar'), ],
            }
        }

    @pytest.fixture
    def create_config(self, tmpdir, simple_config):
        """Create a config file in the tmpdir."""
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(simple_config)

    @pytest.fixture
    def create_command_dirs(self, tmpdir):
        """Create a config file in the tmpdir."""
        os.mkdir(os.path.join(str(tmpdir), "foo"))
        os.mkdir(os.path.join(str(tmpdir), "foo", "bar"))
        os.mkdir(os.path.join(str(tmpdir), "foo", "foobar"))

    @pytest.mark.usefixtures("create_config", "create_command_dirs")
    def test_command_path(self, tmpdir):  # noqa
        config = ConfigIO(str(tmpdir)).load()
        command_path = CommandPath(config)
        expected_path = os.path.join(str(tmpdir), "foo", "foobar")
        actual_paths = [x for x in command_path.items]
        assert [expected_path] == actual_paths
