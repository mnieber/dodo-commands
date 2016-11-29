"""Tests for config.py."""

from dodo_commands.framework.config import ConfigExpander
from dodo_commands.framework.base import CommandError
import pytest


class TestConfigExpander:  # noqa
    simple_config = {
        'ROOT': {
            'command_paths': [
                'foo',
                'bar'
            ]
        },

        'FOO': {
            'bar': {
                'one': 'two'
            },
            'one': [1, 2, 3],
            'two': 2.2
        }
    }

    config_with_eval = {
        'ROOT': {
            'val_EVAL': {
                'one': '(1 + 2 + 3)',
                'two': {
                    'three': '(7 + 8)'
                }
            },
            'one_EVAL': [
                '(1 + 2)',
                '(2 + 3)',
                {
                    'two': {
                        'three': '(7 + 8)'
                    }
                }
            ],
            'two_EVAL': '(10 + 11)'
        }
    }

    config_with_refs = {
        'ROOT': {
            'command_paths': [
                'foo $PATH',
                'bar'
            ]
        },

        'FOO': {
            'bar': {
                'one': '${/ROOT/command_paths/1} and ${/FOO/two}'
            },
            'one': [1, 2, 3],
            'two': '${/FOO/one/2}',
            'three': '${/FOO/one}'
        }
    }

    def test_config_expander(self):
        """Config values are converted into environment variables."""
        config_expander = ConfigExpander()
        config_expander.run(self.simple_config)

    def test_eval(self):
        """
        If a key ends with _EVAL then its value is evaluated.

        (in the following, a value is "simple" if it's not a list or dict)

        If the value is "simple", then it's evaluated with the eval function.
        If the value is a list, then each list item that is "simple" is
        evaluated.
        If the value is a dict, then the value part of each key-value pair
        with a "simple" value is evaluated.
        """
        config_expander = ConfigExpander()
        config_expander.run(self.config_with_eval)

        assert self.config_with_eval['ROOT']['val_EVAL'] == {
            'one': 6,
            'two': {
                'three': '(7 + 8)'
            }
        }
        assert self.config_with_eval['ROOT']['one_EVAL'] == [
            3,
            5,
            {
                'two': {
                    'three': '(7 + 8)'
                }
            }
        ]
        assert self.config_with_eval['ROOT']['two_EVAL'] == 21

    def test_eval_raise(self):
        """If python cannot eval a value then an exception is raised."""
        config_expander = ConfigExpander()
        config_with_eval = dict()
        config_with_eval['FOO'] = {}
        config_with_eval['FOO']['VAL_EVAL'] = "two"
        with pytest.raises(CommandError) as excinfo:
            config_expander.run(config_with_eval)
            assert 'Cannot evaluate value' in str(excinfo.value)

    def test_expand(self):
        """If python cannot eval a value then an exception is raised."""
        config_expander = ConfigExpander()
        config_expander.run(self.config_with_refs)
        assert self.config_with_refs['FOO']['bar']['one'] == 'bar and 3'
        assert self.config_with_refs['FOO']['three'] == '[1, 2, 3]'
        assert "$PATH" not in self.config_with_refs['ROOT']['command_paths'][0]
