from dodo_commands.framework import CommandError, Dodo
from dodo_standard_commands.decorators.docker import (Decorator as
                                                      DockerDecorator)
from dodo_commands.framework.config import expand_keys
from dodo_commands.framework.util import indent
import os
import plumbum
import ruamel.yaml

filters = {}
tests = {}


def register_diagnose_filter(name=None):
    def decorator(func):
        global filters
        filters[name or func.__name__] = func
        return func

    return decorator


def register_diagnose_test(name=None):
    def decorator(func):
        global tests
        tests[name or func.__name__] = func
        return func

    return decorator


@register_diagnose_filter('dodo_expand')
def _dodo_expand(key_str,
                 key=None,
                 layout=None,
                 quote_key=True,
                 quote_val=True,
                 link=None):
    def _quote_val(val):
        if link or not quote_val:
            return val
        return '`' + val + '`'

    def _quote_key(key):
        if link or not quote_key:
            return key
        return '`' + key + '`'

    if key is None:
        key = False

    if link is None:
        link = False

    if "${" not in key_str:
        val = Dodo.get_config(key_str)
        key_str = '${' + key_str + '}'
    else:
        val = expand_keys(Dodo.get_config(), key_str)

    quoted_key_str = _quote_key(key_str)
    val_str = _quote_val(str(val))

    if layout is None:
        layout = isinstance(val, type(dict()))

    result = ""
    if link:
        prefix = "" if os.path.exists(val_str) else "value:"
        result = "`%s <%s%s>`_" % (quoted_key_str, prefix, val_str)
    elif layout:
        if key:
            result += "%s:\n" % quoted_key_str
        result += ("\n\n.. code-block:: yaml\n\n" + indent(
            "# %s\n" % key_str, 4) + indent(
                ruamel.yaml.round_trip_dump(val, indent=4).strip(), amount=4))
    else:
        if key:
            result += "%s = " % quoted_key_str
        result += val_str

    return result


@register_diagnose_filter('leaf')
def _leaf(str_arg):
    return str_arg.split("/")[-1]


def _docker():
    try:
        return plumbum.local['docker']
    except plumbum.commands.processes.CommandNotFound:
        raise CommandError("Docker is not installed")


def _image(key_or_name):
    image = Dodo.get_config(key_or_name, None)
    if not image:
        _, image = DockerDecorator.docker_node(Dodo.get_config, key_or_name,
                                               "")
    return image


@register_diagnose_test('existing_docker_image')
def _is_existing_docker_image(key):
    image = _image(key)
    return _docker()("images", "-q", image)


@register_diagnose_test('existing_container')
def _is_existing_container(key):
    image = _image(key)
    return image in _docker()("ps", "-a", "--filter=name=%s" % image)


@register_diagnose_test('path_exists')
def _path_exists(path):
    return os.path.exists(path)
