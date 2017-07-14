"""Finds a directory or file inside the current project."""
from dodo_commands.system_commands import DodoCommand, CommandError
from dodo_commands.framework.config import CommandPath, ConfigIO, Key, KeyNotFound
import os
from parsimonious import Grammar, ParseError
import re


grammar = Grammar(
    r"""
    api            = cwd? arg* exe_term+
    cwd            = "(" ws? term ws? ")"
    arg            = ws? "[" ws? term ws? "]"
    exe_term       = ws? (formatted_list / term)
    formatted_list = term ws "*" ws term
    term           = ~"[\%\=\-\$\{\}\/\/\._A-Z0-9]*"i
    ws             = ~"\ +"i
    """
)


class Command(DodoCommand):  # noqa
    help = "Creates a new Dodo command."
    safe = False

    @classmethod
    def _find_nodes(cls, node, expr_name, result=None):
        if result is None:
            result = []
        if node:
            if node.expr_name == expr_name:
                result.append(node)
            for child in node.children:
                cls._find_nodes(child, expr_name, result)
        return result

    @classmethod
    def _find_node(cls, node, expr_names):
        if expr_names:
            nodes = cls._find_nodes(node, expr_names[0])
            assert len(nodes) <= 1
            return cls._find_node(nodes[0], expr_names[1:]) if nodes else None
        return node

    def _args(self, args):
        if not args:
            return ""
        return ', '.join(args) + ", "

    @classmethod
    def _term(cls, term):
        def _add_quotes(x):
            return "'%s'" % x if x else None

        def _val(x):
            if (x or '').startswith('='):
                return x[1:]
            return None

        config_keys = {}
        expr = '\$\{([\/\w]+)(\=[\w\$\{\}\/]+)?\}'
        elements = re.split(expr, term)

        i = 0
        while i < len(elements):
            if i % 2 == 0:
                elements[i] = _add_quotes(elements[i])
            else:
                key, val = elements[i], elements[i + 1]
                del elements[i + 1]
                elements[i] = 'self.get_config(%s)' % _add_quotes(key)
                config_keys[key] = _val(val)
            i += 1
        return ' + '.join([x for x in elements if x]), config_keys

    def _write_arguments(self, root_node, a):
        args = []
        for arg_node in self._find_nodes(root_node, 'arg'):
            term_node = self._find_node(arg_node, ['term'])
            arg = term_node.text
            a('        parser.add_argument(\'%s\')' % arg)
            args.append(arg[2:] if arg.startswith('--') else arg)
        if not args:
            a('        pass')
        return args

    @classmethod
    def _format_list(cls, format_string, list_term, a):
        nr_args = format_string.count('%s')
        if nr_args not in [1, 2]:
            raise CommandError("Bad format string: %s" % format_string)

        a('                "%s" %% x for x in %s' % (
            format_string,
            cls._term(list_term)[0] + (".items()" if nr_args == 2 else ""),
        ))

    @classmethod
    def _write_exe_terms(cls, root_node, a, config_keys):
        a('            [')
        for exe_term_node in cls._find_nodes(root_node, 'exe_term'):
            formatted_list_node = cls._find_node(exe_term_node, ['formatted_list'])
            if formatted_list_node:
                list_term, format_string_term = cls._find_nodes(
                    formatted_list_node, 'term'
                )
                a('            ] + ')
                a('            [')
                cls._format_list(format_string_term.text, list_term.text, a)
                a('            ] + ')
                a('            [')
            else:
                term_node = cls._find_node(exe_term_node, ['term'])
                if term_node.text:
                    term, keys = cls._term(term_node.text)
                    config_keys.update(keys)
                    a('                %s,' % term)
        a('            ],')

    @classmethod
    def _write_cwd_term(cls, root_node, a, config_keys):
        cwd_node = cls._find_node(root_node, ['cwd', 'term'])
        if cwd_node:
            term, keys = cls._term(cwd_node.text)
            config_keys.update(keys)
            a('            cwd=%s' % term)

    @classmethod
    def _cast(cls, value):
        for alt_format in [int, float]:
            try:
                return alt_format(value)
            except:
                pass
        return value

    @classmethod
    def _xpath(cls, key):
        return [k for k in key.split("/") if k]

    def _has_config_key(self, xpath):
        try:
            Key(self.config, xpath).get()
            return True
        except KeyNotFound:
            return False

    def _update_config(self, config_keys, config):
        changed = False
        for key, value in config_keys.items():
            xpath = self._xpath(key)
            if self._has_config_key(xpath):
                continue

            node = config
            for idx, branch in enumerate(xpath[:-1]):
                if branch not in node:
                    node[branch] = {}
                node = node[branch]

            node[xpath[-1]] = self._cast(value)
            changed = True

        return changed

    def add_arguments_imp(self, parser):  # noqa
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument('name')
        parser.add_argument(
            '--next-to',
            required=True,
            help='Create the new command at the location of this command'
        )
        parser.add_argument(
            '--parse',
            help='Parse api syntax to create the new command'
        )

    def handle_imp(self, name, next_to, parse, **kwargs):  # noqa
        dest_path = None
        command_path = CommandPath(self.config)
        for item in command_path.items:
            script_path = os.path.join(
                item.full_path, next_to + ".py"
            )
            if os.path.exists(script_path):
                dest_path = os.path.join(
                    item.full_path, name + ".py"
                )

        if not dest_path:
            raise CommandError("Script not found: %s" % next_to)

        if os.path.exists(dest_path):
            raise CommandError("Destination already exists: %s" % dest_path)

        try:
            root_node = grammar.parse(parse) if parse else None
        except ParseError as e:
            raise CommandError("Error while parsing: %s" % e)

        args = []
        config_keys = {}

        with open(dest_path, "w") as f:
            def a(x):
                f.write(x + '\n')

            a('# noqa')
            a('from dodo_commands.system_commands import DodoCommand')
            a('')
            a('')
            a('class Command(DodoCommand):  # noqa')
            a('    help = ""')
            a('')
            a('    def add_arguments_imp(self, parser):  # noqa')
            args = self._write_arguments(root_node, a)
            a('')
            a('    def handle_imp(self, %s**kwargs):  # noqa' % self._args(args))
            a('        self.runcmd(')
            self._write_exe_terms(root_node, a, config_keys)
            self._write_cwd_term(root_node, a, config_keys)
            a('        )')

        config = ConfigIO().load(load_layers=False)
        if self._update_config(config_keys, config):
            ConfigIO().save(config)

        print(dest_path)
