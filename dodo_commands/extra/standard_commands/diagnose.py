from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import bordered
from jinja2 import Environment, FileSystemLoader
import glob
import os
import sphinx  # noqa
import sys
from functools import partial
from importlib import import_module


def _args():
    parser = ArgumentParser(
        description='Create documentation based on the dodo config'
    )
    args = Dodo.parse_args(parser)
    args.src_dir = Dodo.get_config('/DIAGNOSE/src_dir')
    args.output_dir = Dodo.get_config('/DIAGNOSE/output_dir')
    args.project_name = Dodo.get_config('/ROOT/project_name')
    args.filters = Dodo.get_config('/DIAGNOSE/filters', [])
    return args


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
        Dodo.runcmd(['cp', src_conf_file, target_conf_file])
    elif not os.path.exists(target_conf_file):
        Dodo.runcmd(
            [
                'sphinx-quickstart',
                '--project=%s' % args.project_name
            ],
            cwd=args.output_dir
        )


def _sphinx_build(args):
    Dodo.runcmd(
        [
            'sphinx-build',
            '-q',
            '-b',
            'html',
            args.output_dir,
            os.path.join(args.output_dir, 'html'),
        ],
    )


def _open_browser(args):
    Dodo.runcmd(
        [
            'xdg-open',
            os.path.join(args.output_dir, 'html', 'index.html'),
        ],
    )


def _create_jinja_environment(args):
    env = Environment(
        loader=FileSystemLoader(args.src_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # import more filters and tests
    for syspath, basename in args.filters:
        sys.path.append(syspath)
        import_module(basename)
        sys.path.pop()

    env.tests.update(_tests(args))
    env.filters.update(_filters(args))
    return env


def _report_error(errors, error):
    errors.append(error)


def _tests(args):
    result = {}
    from dodo_commands.extra.standard_commands._diagnose_filters_and_tests import tests
    for name, func in tests.items():
        result[name] = partial(func, args)
    return result


def _filters(args):
    result = {}
    from dodo_commands.extra.standard_commands._diagnose_filters_and_tests import filters
    for name, func in filters.items():
        result[name] = partial(func, args)
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
        Dodo.runcmd(['mkdir', '-p', args.output_dir])

    env = _create_jinja_environment(args)

    template_files = _template_files(args)
    for template_file in template_files:
        _render_template(args, env, template_file)

    if errors:
        print("")
        print(
            bordered("Warning, there were errors:") +
            "\n" +
            ("\n".join(errors))
        )
        print("")
    _create_sphinx_conf(args)
    _sphinx_build(args)
    _open_browser(args)
