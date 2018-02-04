# noqa
from dodo_commands.system_commands import DodoCommand
import glob
import os
import sys
import re
from importlib import import_module
import ansimarkup
from dodo_commands.framework.util import bordered
from dodo_commands.framework.config import expand_keys
import textwrap

from ._diagnose_base import DiagnoseBase  # noqa


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle_imp(self, **kwargs):  # noqa
        self.steps_dir = self.get_config('/ROOT/diagnose_dir')

        self.am = ansimarkup.AnsiMarkup(tags=dict(
            orange=ansimarkup.parse("<fg #f29130>"),
            yellow=ansimarkup.parse("<fg #faff00>")
        ))
        self._parse = self.am.parse

        step_files = glob.glob(os.path.join(self.steps_dir, "*.py"))
        for step_index in range(len(step_files) + 1):
            for step_file in step_files:
                step_module_name = os.path.splitext(
                    os.path.basename(step_file)
                )[0]
                if step_module_name.startswith("%d_" % step_index):
                    self.run_step(step_module_name)

    def _expand(self, term):
        return expand_keys(term, self.config)

    def prnt(self, msg, new_line=True):
        paragraphs = re.split('<cr/>', msg)
        for paragraph in paragraphs:
            self.prnt_paragraph(paragraph)
            if new_line:
                sys.stdout.write('\n')

    # Items like `this` are printed in green.
    # Items like ``this`` are printed in yellow.
    # Items like ##this## are expanded to this = that.
    def prnt_paragraph(self, paragraph):
        msg, new_msg = paragraph, ""

        key_val_terms = re.split('\#\#([^\#]+)\#\#', msg)
        for idx, term in enumerate(key_val_terms):
            if idx % 2:
                new_msg += '<yellow>%s = %s</yellow>' % (term, self._expand(term))
            else:
                new_msg += self._expand(term)
        msg, new_msg = new_msg, ""

        yellow_terms = re.split('``([^``]+)``', msg)
        for idx, term in enumerate(yellow_terms):
            if idx % 2:
                new_msg += '<yellow>%s</yellow>' % term
            else:
                new_msg += term
        msg, new_msg = new_msg, ""

        green_terms = re.split('`([^`]+)`', msg)
        for idx, term in enumerate(green_terms):
            if idx % 2:
                new_msg += '<green>%s</green>' % term
            else:
                new_msg += term
        msg, new_msg = new_msg, ""

        sys.stdout.write(textwrap.fill(
            self._parse(msg),
            120
        ))

    def prnt_next(self, msg):
        sys.stdout.write('\n')
        self.prnt("<orange>NEXT: </orange>", new_line=False)
        self.prnt(msg)
        sys.exit(1)

    def prnt_error(self, msg):
        sys.stdout.write('\n')
        self.prnt("<red>ERROR: </red>", new_line=False)
        self.prnt(msg)
        sys.exit(1)

    def run_step(self, step_module_name):
        sys.path.append(self.steps_dir)
        module = import_module(step_module_name)
        diagnose = module.Diagnose(
            get_config=self.get_config,
            prnt=self.prnt,
            prnt_next=self.prnt_next,
            prnt_error=self.prnt_error
        )

        print(bordered(diagnose.title))
        print('')

        diagnose.run()
        print('')
