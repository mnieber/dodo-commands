# -*- coding: utf-8 -*-
"""Utilities."""
from six.moves import input as raw_input
import os
import time
import sys
import re
from plumbum import local


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class classproperty(object):  # noqa
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        """Return read-only property value."""
        return self.f(owner)


def remove_trailing_dashes(args):
    """Removes first -- item from args."""
    return args[1:] if args[:1] == ['--'] else args


def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    if is_windows():
        tl, tr, bl, br, v, h = u'+', u'+', u'+', u'+', u'|', u'-'
    else:
        tl, tr, bl, br, v, h = u'┌', u'┐', u'└', u'┘', u'│', u'─'
    res = [tl + h * width + tr]
    for s in lines:
        res.append(v + (s + ' ' * width)[:width] + v)
    res.append(bl + h * width + br)
    return '\n'.join(res)


def is_using_system_dodo():
    import dodo_commands
    dodo_commands_path = dodo_commands.__path__[0]
    return os.path.realpath(dodo_commands_path) == dodo_commands_path


try:
    import textwrap
    textwrap.indent
except AttributeError:  # undefined function (wasn't added until Python 3.3)

    def indent(text, amount, ch=' '):
        padding = amount * ch
        return ''.join(padding + line for line in text.splitlines(True))
else:

    def indent(text, amount, ch=' '):
        return textwrap.indent(text, amount * ch)


class InvalidIndex(Exception):
    def __init__(self, index):
        super(InvalidIndex, self).__init__('Invalid index')
        self.index = index


def filter_choices(all_choices, raw_choice):
    regexp = r"(\d)+(\-(\d)+)?,?"
    result = []
    span = [None, None]
    for choice in [x for x in re.finditer(regexp, raw_choice)]:
        if span[0] is None:
            span[0] = choice.span()[0]
        if span[1] is None or span[1] == choice.span()[0]:
            span[1] = choice.span()[1]
        from_index = int(choice.group(1)) - 1
        if from_index < 0:
            raise InvalidIndex(from_index)
        to_index = int(choice.group(3)) - 1 if choice.group(3) else from_index
        if to_index >= len(all_choices):
            raise InvalidIndex(to_index)
        for idx in range(from_index, to_index + 1):
            result.append(all_choices[idx])
    return result, span


def is_windows():
    return os.name == 'nt'


def symlink(source, link_name):
    import os
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()


def chop(path):
    while path and path[-1] in ('\n', '\r'):
        path = path[:-1]
    return path


def _log(string):
    with open('/tmp/.dodo.log', 'w') as ofs:
        ofs.write(string + '\n')


def bash_cmd(cmd):
    return ['/bin/bash', '-c', cmd]


class EnvironMemo:
    def __init__(self, extra_vars):
        self.extra_vars = extra_vars
        self.memo = {}

    def __enter__(self):  # noqa
        self.memo = os.environ.copy()
        os.environ.update(self.extra_vars)

    def __exit__(self, type, value, traceback):  # noqa
        os.environ.clear()
        os.environ.update(self.memo)


def exe_exists(exe):
    try:
        local[exe]
        return True
    except:
        return False


def poll_docker_container_status(image_name, dodo_run, condition):
    while True:
        status = dodo_run(bash_cmd('docker ps | grep -i %s' % image_name),
                          capture=True)
        if '(healthy)' in status:
            break
        time.sleep(1)
