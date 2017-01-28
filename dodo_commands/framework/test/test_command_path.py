"""Tests for config.py."""

import pytest
import os
from ..config import ConfigIO, CommandPath


class TestCommandPaths:  # noqa
    simple_config = {
        'ROOT': {
            'command_path': [
                'foo/*',
            ],
            'command_path_exclude': [
                'foo/bar',
            ],
        }
    }

    @pytest.fixture
    def create_config(self, tmpdir):
        """Create a config file in the tmpdir."""
        configIO = ConfigIO(str(tmpdir))  # noqa
        configIO.save(self.simple_config)

    @pytest.fixture
    def create_command_dirs(self, tmpdir):
        """Create a config file in the tmpdir."""
        os.mkdir(os.path.join(str(tmpdir), "foo"))
        os.mkdir(os.path.join(str(tmpdir), "foo", "bar"))
        os.mkdir(os.path.join(str(tmpdir), "foo", "foobar"))

    @pytest.mark.usefixtures("create_config", "create_command_dirs")
    def test_command_path(self, tmpdir):  # noqa
        command_path = CommandPath(str(tmpdir), str(tmpdir))
        expected_path = os.path.join(str(tmpdir), "foo", "foobar")
        actual_paths = [x.full_path for x in command_path.items]
        assert [expected_path] == actual_paths
