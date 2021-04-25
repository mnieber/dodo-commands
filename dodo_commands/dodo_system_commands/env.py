import os
import sys
from contextlib import contextmanager

from dodo_commands import CommandError, Dodo
from dodo_commands.dependencies.get import plumbum
from dodo_commands.framework.global_config import (
    global_config_get,
    load_global_config_parser,
    write_global_config_parser,
)
from dodo_commands.framework.paths import Paths

from ._create_env import forget_env, register_env, register_python_env

local = plumbum.local


def _args():
    Dodo.parser.add_argument("env", nargs="?")

    group = Dodo.parser.add_mutually_exclusive_group()
    group.add_argument("--create-python-env", action="store_true")
    group.add_argument("--use-python-env")
    group.add_argument(
        "--shell",
        help="Use this shell value instead of the global settings.shell value",
    )

    group = Dodo.parser.add_mutually_exclusive_group()
    group.add_argument("--latest", action="store_true", dest="use_latest")
    group.add_argument("--create", action="store_true")
    group.add_argument("--init", action="store_true")
    group.add_argument("--forget", action="store_true")

    args = Dodo.parse_args()
    if args.create_python_env and not (args.create or args.init):
        raise CommandError(
            "The --create-python-env flag should be used together with"
            + " --init or --create"
        )
    return args


@contextmanager
def undo(undo_steps):
    try:
        yield
    except:  # noqa
        for undo_step in undo_steps:
            undo_step()
        raise


class Activator:
    def _report(self, x):
        sys.stderr.write(x)
        sys.stderr.flush()

    def init(self, env, use_latest):
        self.global_config = load_global_config_parser()
        if not self.global_config.has_section("recent"):
            self.global_config.add_section("recent")

        self.latest_env = global_config_get(self.global_config, "recent", "latest_env")
        self.shell = args.shell or global_config_get(
            self.global_config, "settings", "shell", "bash"
        )

        if env == "-":
            env = global_config_get(self.global_config, "recent", "previous_env")
            if not env:
                raise CommandError("There is no previous environment")

        if use_latest:
            if env:
                self._report("Options --latest and <env> are mutually exclusive\n")
                return False
            env = self.latest_env
            if not env:
                self._report("There is no latest environment\n")
                return False

        self.env = env
        self.env_dir = Paths().env_dir(self.env) if self.env else None

        return True

    def _config_dir(self, project_dir):
        return os.path.join(project_dir, ".dodo_commands")

    def _python_env_dir(self, create_python_env, use_python_env, project_dir):
        if use_python_env:
            return os.path.realpath(os.path.abspath(use_python_env))
        if create_python_env:
            return os.path.join(project_dir, ".env")
        return None

    def run(self, init, create, create_python_env, use_python_env, forget):
        if create:
            project_dir = os.path.expanduser(
                os.path.join(
                    self.global_config.get("settings", "projects_dir"), self.env
                )
            )
        elif init or create_python_env:
            project_dir = os.path.abspath(local.cwd)
        elif forget:
            pass
        else:
            if not os.path.exists(self.env_dir):
                raise CommandError(
                    "Environment not found: %s. Use the --create flag to create it\n"
                    % self.env
                )

        undo_steps = []
        with undo(undo_steps):
            if create or init:
                if os.path.exists(self.env_dir):
                    self._report(
                        "Cannot create an environment because the "
                        + "directory already exists: %s\n" % self.env_dir
                    )
                    return False

                verb = "Creating" if create else "Initializing in existing"
                self._report("%s project directory %s ..." % (verb, project_dir))
                config_dir = self._config_dir(project_dir)
                register_env(
                    self.env,
                    project_dir,
                    config_dir,
                    self._python_env_dir(
                        create_python_env, use_python_env, project_dir
                    ),
                    undo_steps,
                )

            if create_python_env:
                register_python_env(
                    self.global_config.get("settings", "python_interpreter"),
                    self.env,
                    self._python_env_dir(
                        create_python_env, use_python_env, project_dir
                    ),
                    undo_steps,
                )

            if forget:
                forget_env(self.env)
                self.env = "default"

            if create or init or create_python_env:
                self._report(" done\n")

        if self.env != self.latest_env:
            self.global_config.set("recent", "previous_env", self.latest_env)
            self.global_config.set("recent", "latest_env", self.env)
            write_global_config_parser(self.global_config)

        activate_filename = os.path.join(self.env_dir, "activate.%s" % self.shell)

        if not forget:
            sys.stdout.write("source %s\n" % activate_filename)


if Dodo.is_main(__name__, safe=False):
    args = _args()
    if not args.env and not args.use_latest:
        raise CommandError("No environment was specified")

    activator = Activator()
    if activator.init(args.env, args.use_latest):
        activator.run(
            args.init,
            args.create,
            args.create_python_env,
            args.use_python_env,
            args.forget,
        )
