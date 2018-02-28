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

# -*- coding: utf-8 -*-

"""Base classes for writing management commands."""

from __future__ import unicode_literals

import os
import sys
import argcomplete
from argparse import ArgumentParser, SUPPRESS
from dodo_commands.framework.config import (
    look_up_key, load_dodo_config
)
from dodo_commands.framework.command_error import CommandError


class CommandParser(ArgumentParser):  # noqa
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """
    def __init__(self, cmd, **kwargs):  # noqa
        self.cmd = cmd
        super(CommandParser, self).__init__(**kwargs)

    def error(self, message):  # noqa
        if self.cmd._called_from_command_line:
            super(CommandParser, self).error(message)
        else:
            raise CommandError("Error: %s" % message)


class BaseCommand(object):  # noqa
    """
    The base class from which all management commands ultimately
    derive.
    """
    # Metadata about this command.
    help = ''
    args = ''

    # Configuration shortcuts that alter various logic.
    _called_from_command_line = False
    can_import_settings = True

    def __init__(self, name):
        self.config = load_dodo_config()
        self.name = name

    def usage(self, subcommand):  # noqa
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.
        """
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand):  # noqa
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        parser = CommandParser(
            self, prog="%s %s" % (os.path.basename(prog_name), subcommand),
            description=self.help or None)
        parser.add_argument(
            '--traceback', action='store_true',
            help=SUPPRESS)
        if self.args:
            # Keep compatibility and always accept positional arguments,
            # like optparse when args is set
            parser.add_argument('args', nargs='*')
        self.add_arguments(parser)
        argcomplete.autocomplete(parser)

        return parser

    def add_arguments(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def print_help(self, prog_name, subcommand):  # noqa
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv, subcommand):  # noqa
        """
        Set up any environment changes requested (e.g., Python path
        and Django settings), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``CommandError``, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], subcommand)

        options = parser.parse_args(argv[2:])

        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        try:
            self.handle(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise

            sys.stderr.write('%s: %s\n' % (e.__class__.__name__, e))
            sys.exit(1)

    def get_config(self, key, default_value="__not_set_234234__"):  # noqa
        return look_up_key(self.config, key, default_value)

    def handle(self, *args, **options):  # noqa
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError(
            'subclasses of BaseCommand must provide a handle() method')
