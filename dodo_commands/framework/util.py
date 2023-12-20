# -*- coding: utf-8 -*-
"""Utilities."""
import os
import re
import sys

from dodo_commands.dependencies.get import plumbum, six

raw_input = six.moves.input


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
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


class classproperty(object):  # noqa
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        """Return read-only property value."""
        return self.f(owner)


def bordered(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    tl, tr, bl, br, v, h = "┌", "┐", "└", "┘", "│", "─"
    res = [tl + h * width + tr]
    for s in lines:
        res.append(v + (s + " " * width)[:width] + v)
    res.append(bl + h * width + br)
    return "\n".join(res)


def is_using_system_dodo():
    import dodo_commands

    dodo_commands_path = dodo_commands.__path__[0]
    return os.path.realpath(dodo_commands_path) == dodo_commands_path


try:
    import textwrap

    textwrap.indent
except AttributeError:  # undefined function (wasn't added until Python 3.3)

    def indent(text, amount, ch=" "):
        padding = amount * ch
        return "".join(padding + line for line in text.splitlines(True))

else:

    def indent(text, amount, ch=" "):
        return textwrap.indent(text, amount * ch)


def make_executable(script_filename):
    st = os.stat(script_filename)
    os.chmod(script_filename, st.st_mode | 0o111)


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
    while path and path[-1] in ("\n", "\r"):
        path = path[:-1]
    return path


def _log(string):
    with open("/tmp/.dodo.log", "a") as ofs:
        ofs.write(string + "\n")


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
        plumbum.local[exe]
        return True
    except plumbum.commands.processes.CommandNotFound:
        return False


class classproperty(property):  # noqa
    def __get__(self, cls, owner):  # noqa
        return classmethod(self.fget).__get__(None, owner)()


def maybe_list_to_list(maybe_list):
    return maybe_list if isinstance(maybe_list, list) else [maybe_list]


def to_arg_list(x):
    if isinstance(x, str):
        if re.match(r"'.*'", x) or re.match(r'".*"', x):
            x = x[1:-1]
        x = x.split()
    return [
        (
            f"--{arg[2:]}"
            if arg.startswith("++")
            else f"-{arg[1:]}"
            if arg.startswith("+")
            else arg
        )
        for arg in maybe_list_to_list(x or [])
    ]


def sh_cmd(cmd):
    return ["sh", "-c", cmd]


def xpath_to_string(xpath):
    return "/" + "/".join([str(x) for x in xpath])
