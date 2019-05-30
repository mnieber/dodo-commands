"""Module for working with the dodo configurations."""

from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.config_expander import ConfigExpander
from dodo_commands.framework.config_expander import Key, KeyNotFound  # noqa
from dodo_commands.framework.util import symlink
from plumbum import local
from six.moves import configparser
import glob
from fnmatch import fnmatch
import hashlib
import json
import os
import argparse
from os.path import dirname
import re
import ruamel.yaml
import sys

try:
    from dotenv import dotenv_values
except ImportError:
    # Stub
    def dotenv_values(x):
        raise CommandError(
            "Package python-dotenv not installed. Please run: pip install python-dotenv."
        )


def _is_windows():
    return os.name == 'nt'


def _ext():
    return '.exe' if _is_windows() else ''


class Paths:
    # Cached result of finding the current project dir
    _project_dir = None

    def __init__(self, project_dir=None):
        self._project_dir = project_dir or Paths._project_dir
        if not self._project_dir:
            bin_dir = os.path.realpath(dirname(sys.executable))
            marker_file = os.path.join(bin_dir, '.dodo_project_dir_marker')
            Paths._project_dir = (dirname(dirname(dirname(bin_dir)))
                                  if os.path.exists(marker_file) else "")
            self._project_dir = Paths._project_dir

    def home_dir(self, expanduser=True):
        return os.path.expanduser('~') if expanduser else '~'

    def global_config_dir(self, expanduser=True):
        return os.path.join(self.home_dir(expanduser), '.dodo_commands')

    def global_config_filename(self):
        return os.path.join(self.global_config_dir(), 'config')

    def default_commands_dir(self, expanduser=True):
        return os.path.join(self.global_config_dir(expanduser),
                            'default_commands')

    def global_commands_dir(self, expanduser=True):
        return os.path.join(self.global_config_dir(expanduser), 'commands')

    def virtual_env_dir(self):
        return os.path.join(self.project_dir(), 'dodo_commands', 'env')

    def virtual_env_bin_dir(self):
        return os.path.join(self.virtual_env_dir(),
                            'Scripts' if _is_windows() else 'bin')

    def pip(self):
        return os.path.join(self.virtual_env_bin_dir(), 'pip' + _ext())

    def site_packages_dir(self):
        python = local[os.path.join(self.virtual_env_bin_dir(),
                                    "python" + _ext())]

        result = python(
            "-c", "from distutils.sysconfig import get_python_lib; " +
            "print(get_python_lib())")
        while result[-1] in ['\n', '\r']:
            result = result[:-1]
        return result

    def project_dir(self):
        """Return the root dir of the current project."""
        return self._project_dir

    def res_dir(self):
        return os.path.join(self.project_dir(), "dodo_commands", "res")

    def package_dir(self):
        import dodo_commands
        return os.path.dirname(dodo_commands.__file__)

    def extra_dir(self):
        return os.path.join(self.package_dir(), "extra")


def load_global_config_parser():
    config_parser = configparser.ConfigParser()
    config_parser.read(Paths().global_config_filename())
    return config_parser


def write_global_config_parser(config_parser):
    """Save configuration."""
    with open(Paths().global_config_filename(), "w") as f:
        config_parser.write(f)


def projects_dir():
    return os.path.expanduser(load_global_config_parser().get(
        "settings", "projects_dir"))


_global_config = """[settings]
projects_dir=~/projects
python_interpreter=python
diff_tool=diff

[recent]
"""


def _touch_init_py(dir_name):
    init_py = os.path.join(dir_name, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, 'w'):
            pass


def create_global_config():
    """Create config file and default_commands dir."""
    base_dir = Paths().global_config_dir()
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    config_filename = Paths().global_config_filename()
    if not os.path.exists(config_filename):
        with open(config_filename, 'w') as f:
            f.write(_global_config)

    default_commands_dir = Paths().default_commands_dir()
    if not os.path.exists(default_commands_dir):
        os.mkdir(default_commands_dir)
        _touch_init_py(default_commands_dir)
        symlink(
            os.path.join(Paths().extra_dir(), "dodo_standard_commands"),
            os.path.join(Paths().default_commands_dir(),
                         "dodo_standard_commands"))

    global_commands_dir = Paths().global_commands_dir()
    if not os.path.exists(global_commands_dir):
        os.mkdir(global_commands_dir)
        _touch_init_py(global_commands_dir)


def merge_into_config(config, layer, xpath=None):
    def _is_list(x):
        return isinstance(x, type(list()))

    def _is_dict(x):
        return isinstance(x, type(dict()))

    def _raise(xpath):
        raise CommandError("Cannot merge configurations. Check key /%s" %
                           '/'.join(new_xpath))

    xpath = xpath or []
    for key, val in (layer or {}).items():
        new_xpath = xpath + [key]

        if key not in config:
            config[key] = val
        elif _is_dict(val):
            if not _is_dict(config[key]):
                _raise(new_xpath)
            merge_into_config(config[key], val, new_xpath)
        elif _is_list(val):
            if not _is_list(config[key]):
                _raise(new_xpath)
            config[key].extend(val)
        else:
            config[key] = val


class ConfigIO:
    """Read and write the dodo configuration."""

    def __init__(self, config_base_dir=None):
        """Arg config_base_dir is where config files are searched.

        Arg config_base_dir defaults to Paths().res_dir().
        """
        self.config_base_dir = (Paths().res_dir() if config_base_dir is None
                                else config_base_dir)

    def _path_to(self, post_fix_paths):
        """Return path composed of config_base_dir and post_fix_paths list."""
        return os.path.join(self.config_base_dir, *post_fix_paths)

    def glob(self, patterns):
        """Returns list of filenames"""

        def add_prefix(filename):
            return (filename
                    if filename.startswith('/') else self._path_to([filename]))

        patterns = [
            add_prefix(os.path.expanduser(pattern)) for pattern in patterns
        ]

        result = []
        for pattern in patterns:
            result.extend([x for x in glob.glob(pattern)])
        return result

    def load(self, config_filename='config.yaml'):
        """Get configuration."""
        full_config_filename = self._path_to([config_filename])
        if not os.path.exists(full_config_filename):
            return None

        with open(full_config_filename) as f:
            config = ruamel.yaml.round_trip_load(f.read())
        return config

    def save(self, config, config_filename='config.yaml'):
        """Write config to config_filename."""
        with open(self._path_to([config_filename]), 'w') as f:
            return f.write(ruamel.yaml.round_trip_dump(config))


class ConfigLoader:
    """Load the project's dodo config and expand it."""

    def __init__(self, config_io=None):
        self.config_io = config_io or ConfigIO()

    def _add_to_config(self, config, section, key, value):
        if section in config:
            if key not in config[section]:
                config[section][key] = value

    def _system_commands_dir(self):
        """Return directory where system command scripts are stored"""
        import dodo_commands.dodo_system_commands
        return os.path.dirname(dodo_commands.dodo_system_commands.__file__)

    def _extend_config(self, config):
        """Add special values to the project's config"""
        project_dir = Paths().project_dir()
        if project_dir:
            self._add_to_config(config, "ROOT", "project_name",
                                os.path.basename(project_dir))
            self._add_to_config(config, "ROOT", "project_dir", project_dir)
            self._add_to_config(config, "ROOT", "res_dir", Paths().res_dir())

    def _extend_command_path(self, config):
        """Add the system commands to the command path"""
        self._add_to_config(config, "ROOT", "command_path", [])
        config['ROOT']['command_path'].append(self._system_commands_dir())
        if not Paths().project_dir():
            config['ROOT']['command_path'].append(
                os.path.join(Paths().default_commands_dir(), '*'))

    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    def get_layers(self, config):
        layer_filenames = []
        for pattern in config.get('ROOT', {}).get('layers', []):
            filenames = self.config_io.glob([pattern])
            if not filenames:
                print("Warning, no layers found for pattern: %s" % pattern)
            layer_filenames.extend(filenames)

        parser = argparse.ArgumentParser()
        parser.add_argument('--layer', action='append', help=argparse.SUPPRESS)
        args, _ = parser.parse_known_args(
            [x for x in sys.argv if x not in ('--help', '-h')])
        extra_layers = args.layer or []

        for extra_layer_filename in self.config_io.glob(extra_layers):
            # Remove layers in the same group, because by definition
            # we should not use both foo.bar.yaml and foo.baz.yaml.
            parts = os.path.basename(extra_layer_filename).split('.')
            if len(parts) == 3:
                pattern = os.path.join(os.path.dirname(extra_layer_filename),
                                       parts[0] + '.*.*')
                layer_filenames = [
                    x for x in layer_filenames if not fnmatch(x, pattern)
                ]

            if extra_layer_filename not in layer_filenames:
                layer_filenames.append(extra_layer_filename)

        return layer_filenames

    def load(self, extend=True):
        fallback_config = dict(ROOT={})
        try:
            config = self.config_io.load() or fallback_config
            for layer_filename in self.get_layers(config):
                layer = self.config_io.load(layer_filename)
                merge_into_config(config, layer)

        except ruamel.yaml.scanner.ScannerError:
            config = fallback_config
            self._report(
                "There was an error while loading the configuration. "
                "Run 'dodo diff' to compare your configuration to the "
                "default one.\n")

        if extend:
            self._extend_command_path(config)
            self._extend_config(config)

        extra_vars = dict()

        def _load_env(dotenv_file):
            if not os.path.exists(dotenv_file):
                self._report("Dotenv file not found: %s\n" % dotenv_file)
            extra_vars.update(dotenv_values(dotenv_file))

        # Call dotenv_values for every item of /ENV/dotenv
        callbacks = {}
        for idx, _ in enumerate(config['ROOT'].get('dotenv_files', [])):
            callbacks['/ROOT/dotenv_files/%d' % idx] = _load_env

        ConfigExpander(extra_vars).run(config, callbacks=callbacks)
        return config


class CommandPath:
    """Read search paths for command scripts from the configuration."""

    def __init__(self, include_patterns, exclude_patterns):
        excluded_command_dirs = self._create_items(exclude_patterns)

        self.items = sorted([
            x for x in self._create_items(include_patterns)
            if x not in excluded_command_dirs
        ])

        basenames = [os.path.basename(x) for x in self.items]
        for basename in basenames:
            if basenames.count(basename) > 1:
                raise CommandError("More than 1 command path with name %s" %
                                   basename)

    def _create_items(self, patterns):
        result = []
        for pattern in patterns:
            for x in glob.glob(os.path.expanduser(pattern)):
                if os.path.isdir(
                        x) and not os.path.basename(x).startswith('_'):
                    result.append(x)
        return result

    def _create_search_path_dir(self):
        hash_code = hashlib.md5(json.dumps(
            self.items).encode('utf-8')).hexdigest()
        search_path_dir = os.path.join(Paths().global_config_dir(),
                                       "search_path", hash_code)

        if not os.path.exists(search_path_dir):
            os.makedirs(search_path_dir)
            open(os.path.join(search_path_dir, "__init__.py"), 'a').close()
            for item in self.items:
                basename = os.path.basename(item)
                target_path = os.path.join(search_path_dir, basename)
                if not os.path.exists(target_path):
                    symlink(item, target_path)

        return search_path_dir

    def extend_sys_path(self):
        search_path_dir = self._create_search_path_dir()
        if search_path_dir not in sys.path:
            sys.path.append(search_path_dir)


def expand_keys(config, text):
    result = ""
    val_terms = re.split('\$\{([^\}]+)\}', text)
    for idx, term in enumerate(val_terms):
        if idx % 2:
            xpath = [k for k in term.split("/") if k]
            str_rep = json.dumps(Key(config, xpath).get())
            if str_rep.startswith('"') and str_rep.endswith('"'):
                str_rep = str_rep[1:-1]
            result += str_rep
        else:
            result += term
    return result


def get_command_path(config=None):
    config = config or ConfigLoader().load()
    root_config = config.get('ROOT', {})
    command_path = root_config.get('command_path', [])
    command_path_exclude = root_config.get('command_path_exclude', [])
    return CommandPath(include_patterns=command_path,
                       exclude_patterns=command_path_exclude)
