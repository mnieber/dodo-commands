# noqa
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import bordered
from jinja2 import Environment, FileSystemLoader
import glob
import os
import sphinx  # noqa
import sys
from functools import partial
from importlib import import_module


class Command(DodoCommand):  # noqa
    help = ""
    safe = False

    def add_arguments_imp(self, parser):  # noqa
        pass

    def _template_files(self):
        result = []
        for step_file in glob.glob(os.path.join(self.src_dir, "*.rst")):
            template_file = os.path.basename(step_file)
            result.append(template_file)
        return result

    def _create_sphinx_conf(self):
        target_conf_file = os.path.join(self.output_dir, 'conf.py')
        src_conf_file = os.path.join(self.src_dir, 'conf.py')
        if os.path.exists(src_conf_file):
            self.runcmd(['cp', src_conf_file, target_conf_file])
        elif not os.path.exists(target_conf_file):
            self.runcmd(
                [
                    'sphinx-quickstart',
                    '--project=%s' % self.get_config('/ROOT/project_name')
                ],
                cwd=self.output_dir
            )

    def _sphinx_build(self):
        self.runcmd(
            [
                'sphinx-build',
                '-q',
                '-b',
                'html',
                self.output_dir,
                os.path.join(self.output_dir, 'html'),
            ],
        )

    def _open_browser(self):
        self.runcmd(
            [
                'xdg-open',
                os.path.join(self.output_dir, 'html', 'index.html'),
            ],
        )

    def _create_jinja_environment(self):
        self.env = Environment(
            loader=FileSystemLoader(self.src_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # import more filters and tests
        for syspath, basename in self.get_config('/DIAGNOSE/filters', []):
            sys.path.append(syspath)
            import_module(basename)
            sys.path.pop()

        self.env.tests.update(self._tests())
        self.env.filters.update(self._filters())

    def _report_error(self, error):
        self.errors.append(error)

    def _tests(self):
        result = {}
        from dodo_commands.extra.standard_commands._diagnose_filters_and_tests import tests
        for name, func in tests.items():
            result[name] = partial(func, self)
        return result

    def _filters(self):
        result = {}
        from dodo_commands.extra.standard_commands._diagnose_filters_and_tests import filters
        for name, func in filters.items():
            result[name] = partial(func, self)
        return result

    def handle_imp(self, **kwargs):  # noqa
        self.errors = []
        self.src_dir = self.get_config('/DIAGNOSE/src_dir')
        self.output_dir = self.get_config('/DIAGNOSE/output_dir')
        if not os.path.exists(self.output_dir):
            self.runcmd(['mkdir', '-p', self.output_dir])

        self._create_jinja_environment()

        template_files = self._template_files()
        for template_file in template_files:
            self._render_template(template_file)

        if self.errors:
            print("")
            print(
                bordered("Warning, there were errors:") +
                "\n" +
                ("\n".join(self.errors))
            )
            print("")
        self._create_sphinx_conf()
        self._sphinx_build()
        self._open_browser()

    def _render_template(self, template_file):
        template = self.env.get_template(template_file)
        output = template.render()
        rst_file = os.path.join(self.output_dir, template_file)
        with open(rst_file, 'w') as ofs:
            ofs.write(output)
