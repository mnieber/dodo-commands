# This file is based on source code from the Django Software Foundation,
# using the following license:

# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,          # noqa
# are permitted provided that the following conditions are met:

#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.

#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.

#     3. Neither the name of Django nor the names of its contributors may be used           # noqa
#        to endorse or promote products derived from this software without
#        specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND           # noqa
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR           # noqa
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES            # noqa
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON            # noqa
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Root of the framework module."""

import argcomplete
from argparse import ArgumentParser
from collections import defaultdict
import ruamel.yaml
import os
import pkgutil
import subprocess
import sys
import traceback
from importlib import import_module
from dodo_commands.framework.util import query_yes_no
from dodo_commands.framework.config import (
    CommandPath, get_project_dir, load_dodo_config
)
from dodo_commands.framework.base import (
    BaseCommand, CommandError
)


def get_version():  # noqa
    return "0.13.4"


def find_commands(module_dir):
    """
    Return a list of all the command names.

    Given a path to a dodo_commands directory, returns a list of all the
    command names that are available.

    Returns an empty list if no commands are defined.
    """
    return [
        name for _, name, is_pkg in pkgutil.iter_modules([module_dir])
        if not is_pkg and not name.startswith('_')
    ]


def load_command_class(module_dir, name):
    """
    Return the Command class instance for module_dir and name.

    Given a command name and module directory, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    """
    def install_packages(meta_data_filename):
        """Pip install packages found in meta_data_filename."""
        with open(meta_data_filename) as f:
            meta_data = ruamel.yaml.round_trip_load(f.read())
            print("This command wants to install additional packages:\n")
            print(meta_data['requirements'])
            if query_yes_no("Install (yes), or abort (no)?"):
                print("\n--- Installing from %s ---" % meta_data_filename)
                pip = os.path.join(
                    get_project_dir(),
                    "dodo_commands/env/bin/pip"
                )
                subprocess.check_call(
                    [pip, "install"] + meta_data['requirements'])
                print("--- Done ---\n\n")
            else:
                sys.exit(1)

    package_path = module_dir.replace("/", ".")
    import_path = '%s.%s' % (package_path, name)
    if module_dir in ("", None, "."):
        import_path = name

    try:
        module = import_module(import_path)
    except ImportError as e:
        try:
            base_path = import_module(package_path).__path__[0]
            meta_data_filename = os.path.join(base_path, name + ".meta")
            if os.path.exists(meta_data_filename):
                install_packages(meta_data_filename)
                module = import_module(import_path)
            else:
                print(traceback.print_exc(e))
                sys.exit(1)
        except ImportError as e:
            print(traceback.print_exc(e))
            sys.exit(1)

    return module.Command(name)


def get_commands():
    """
    Return a dictionary mapping command names to their Python module directory.

    The dictionary is in the format {command_name: module_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_command_class(module_name, command_name)
    """
    commands = {}
    command_path = CommandPath(load_dodo_config())
    command_path.extend_sys_path()
    for item in command_path.items:
        for command in find_commands(item.full_path):
            commands[command] = item.module_path
    return commands


def call_command(name, *args, **options):
    """
    Call the given command, with the given options and args/kwargs.

    This is the primary API you should use for calling specific commands.
    """
    # Load the command object.
    try:
        module_name = get_commands()[name]
    except KeyError:
        raise CommandError("Unknown command: %r" % name)

    if isinstance(module_name, BaseCommand):
        # If the command is already loaded, use it directly.
        command = module_name
    else:
        command = load_command_class(module_name, name)

    # Simulate argument parsing to get the option defaults.
    parser = command.create_parser('', name)
    # Use the `dest` option name from the parser option
    opt_mapping = {
        sorted(
            s_opt.option_strings
        )[0].lstrip('-').replace('-', '_'): s_opt.dest
        for s_opt in parser._actions if s_opt.option_strings
    }
    arg_options = {
        opt_mapping.get(key, key): value
        for key, value in options.items()
    }
    defaults = parser.parse_args(args=args)
    defaults = dict(defaults._get_kwargs(), **arg_options)
    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop('args', ())

    return command.handle(*args, **defaults)


class ManagementUtility(object):
    """Internal helper class for executing commands."""

    def __init__(self, argv):  # noqa
        self.argv = argv
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, commands_only=False, commands=None):
        """Return the script's main help text, as a string."""
        if commands is None:
            commands = get_commands()

        if commands_only:
            usage = sorted(commands.keys())
        else:
            usage = [
                "",
                "Version %s (%s --version)." % (
                    get_version(), self.prog_name
                ),
                "Type '%s help <subcommand>' for help on "
                "a specific subcommand." % self.prog_name,
                "Available subcommands (dodo help --commands):",
            ]
            commands_dict = defaultdict(lambda: [])
            for name, app in commands.items():
                app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
            for app in sorted(commands_dict.keys()):
                usage.append("")
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)

        return '\n'.join(usage)

    def fetch_command(self, subcommand, commands=None):
        """
        Fetch the given subcommand.

        Tries to fetch the given subcommand, printing a message with the
        appropriate command called from the command line if it can't be found.
        """
        # Get commands outside of try block to prevent swallowing exceptions
        if commands is None:
            commands = get_commands()

        if subcommand not in commands:
            print("Unknown dodo command: %s" % subcommand)
            sys.exit(1)

        module_name = commands[subcommand]
        if isinstance(module_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = module_name
        else:
            klass = load_command_class(module_name, subcommand)
        return klass

    def execute(self):
        """
        Execute subcommand.

        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        commands = get_commands()

        if "_ARGCOMPLETE" in os.environ:
            words = os.environ['COMP_LINE'].split()
            subcommand = words[1]

            if subcommand not in commands:
                parser = ArgumentParser()
                parser.add_argument(
                    'command',
                    choices=[x for x in commands.keys()]
                )
                argcomplete.autocomplete(parser)

            os.environ['COMP_LINE'] = ' '.join(words[:1] + words[2:])
            os.environ['COMP_POINT'] = str(
                int(os.environ['COMP_POINT']) - (len(subcommand) + 1)
            )
        else:
            try:
                subcommand = self.argv[1]
            except IndexError:
                subcommand = 'help'  # Display help if no arguments were given.

        args = self.argv[2:]

        if subcommand == '--version':
            sys.stdout.write(get_version() + '\n')
        elif subcommand == 'help':
            if '--commands' in args:
                sys.stdout.write(
                    self.main_help_text(
                        commands_only=True, commands=commands
                    ) + '\n'
                )
            elif len(args) < 1:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(
                    args[0], commands
                ).print_help(self.prog_name, args[0])
        else:
            self.fetch_command(subcommand, commands).run_from_argv(
                self.argv, subcommand
            )


def execute_from_command_line(argv):
    """A simple method that runs a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
