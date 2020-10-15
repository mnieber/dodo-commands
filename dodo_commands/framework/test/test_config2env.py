"""Tests for config.py."""

from ..config import ConfigExpander


class TestConfigExpander:  # noqa
    simple_config = {
        "ROOT": {"command_path": ["foo", "bar"]},
        "FOO": {"bar": {"one": "two"}, "one": [1, 2, 3], "two": 2.2},
    }

    config_with_refs = {
        "ROOT": {"command_path": ["foo $PATH", "bar"]},
        "FOO": {
            "bar": {"one": "${/ROOT/command_path/1} and ${/FOO/two}"},
            "one": [1, 2, 3],
            "two": "${/FOO/one/2}",
            "three": "${/FOO/one}",
        },
    }

    def test_config_expander(self):
        """Config values are converted into environment variables."""
        config_expander = ConfigExpander()
        config_expander.run(self.simple_config)

    def test_expand(self):
        """dodo/system environment variables are expanded."""
        config_expander = ConfigExpander()
        config_expander.run(self.config_with_refs)
        assert self.config_with_refs["FOO"]["bar"]["one"] == "bar and 3"
        assert self.config_with_refs["FOO"]["three"] == "[1, 2, 3]"
        assert "$PATH" not in self.config_with_refs["ROOT"]["command_path"][0]
