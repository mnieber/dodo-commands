from argparse import ArgumentParser
from dodo_commands.framework import Dodo, ConfigArg, CommandError
from dodo_commands.framework.util import bordered
from importlib import import_module
from jinja2 import Environment, FileSystemLoader
import glob
import os
import sphinx  # noqa
import sys


def _args():
    parser = ArgumentParser(
        description='Create documentation based on the dodo config')
    return Dodo.parse_args(
        parser,
        config_args=[
            ConfigArg('/DIAGNOSE/src_dir', 'src_dir'),
            ConfigArg('/DIAGNOSE/output_dir', 'output_dir'),
            ConfigArg('/ROOT/project_name', 'project_name'),
            ConfigArg('/DIAGNOSE/filters', '--filters', nargs='+', default=[])
        ])


def _template_files(args):
    result = []
    for step_file in glob.glob(os.path.join(args.src_dir, "*.rst")):
        template_file = os.path.basename(step_file)
        result.append(template_file)
    return result


def _create_sphinx_conf(args):
    target_conf_file = os.path.join(args.output_dir, 'conf.py')
    src_conf_file = os.path.join(args.src_dir, 'conf.py')
    if os.path.exists(src_conf_file):
        Dodo.run(['cp', src_conf_file, target_conf_file])
    elif not os.path.exists(target_conf_file):
        Dodo.run(['sphinx-quickstart',
                  '--project=%s' % args.project_name],
                 cwd=args.output_dir)


def _sphinx_build(args):
    Dodo.run([
        'sphinx-build',
        '-q',
        '-b',
        'html',
        args.output_dir,
        os.path.join(args.output_dir, 'html'),
    ], )


def _open_browser(args):
    Dodo.run([
        'xdg-open',
        os.path.join(args.output_dir, 'html', 'index.html'),
    ], )


def _create_jinja_environment(args):
    env = Environment(
        loader=FileSystemLoader(args.src_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # import more filters and tests
    for syspath, basename in args.filters:
        sys.path.append(syspath)
        try:
            import_module(basename)
        except ImportError as e:
            raise CommandError("Could not import filters from %s. Details: %s"
                               % (os.path.join(syspath, basename), e))
        sys.path.pop()

    env.tests.update(_tests())
    env.filters.update(_filters())
    return env


def _report_error(errors, error):
    errors.append(error)


def _tests():
    result = {}
    from dodo_standard_commands._diagnose_filters_and_tests import tests
    for name, func in tests.items():
        result[name] = func
    return result


def _filters():
    result = {}
    from dodo_standard_commands._diagnose_filters_and_tests import filters
    for name, func in filters.items():
        result[name] = func
    return result


def _render_template(args, env, template_file):
    template = env.get_template(template_file)
    output = template.render()
    rst_file = os.path.join(args.output_dir, template_file)
    with open(rst_file, 'w') as ofs:
        ofs.write(output)


if Dodo.is_main(__name__, safe=False):
    args = _args()

    errors = []
    if not os.path.exists(args.output_dir):
        Dodo.run(['mkdir', '-p', args.output_dir])

    env = _create_jinja_environment(args)

    template_files = _template_files(args)
    for template_file in template_files:
        _render_template(args, env, template_file)

    if errors:
        print("")
        print(
            bordered("Warning, there were errors:") + "\n" +
            ("\n".join(errors)))
        print("")
    _create_sphinx_conf(args)
    _sphinx_build(args)
    _open_browser(args)
