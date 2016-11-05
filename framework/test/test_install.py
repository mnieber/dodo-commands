"""Tests for config.py."""
from plumbum import local
from plumbum.cmd import cp
import os

class TestInstall:  # noqa
    def run_install(self, tmpdir):  # noqa
        local['bash'](
            './dodo_commands/bin/install.sh',
            '--projects_dir',
            str(tmpdir)
        )

    def install_defaults(self):  # noqa
        local['python'](
            './dodo_commands/bin/dodo-install-defaults',
            '--ln',
            '--projects',
            './dodo_commands/extra/tutorial_projects'
        )

    def activate_project(self):  # noqa
        local['python'](
            './dodo_commands/bin/dodo-activate',
            'dodo_tutorial',
            '--create'
        )

    def run_cmake(self, tmpdir):  # noqa
        with local.cwd(str(tmpdir)):
            log_filename = "cmake.log"
            (local['dodo_tutorial/env/bin/python'] > log_filename)(
                'dodo_tutorial/env/bin/dodo', 'cmake', '--echo'
            )
            with open(log_filename) as f:
                return f.read()

    def test_save(self, tmpdir):  # noqa
        test_dir = os.path.dirname(__file__)
        framework_dir = os.path.dirname(test_dir)
        system_dir = os.path.dirname(framework_dir)

        cp("-rf", system_dir, tmpdir)
        with local.cwd(tmpdir):
            self.run_install(tmpdir)
            assert os.path.exists('./dodo_commands/dodo_commands.config')

            self.install_defaults()
            assert os.path.exists(
                './dodo_commands/defaults/commands/standard_commands'
            )
            assert os.path.exists(
                './dodo_commands/defaults/projects/tutorial_projects'
            )

            self.activate_project()
            assert os.path.exists('dodo_tutorial/env/bin')

            result = self.run_cmake(tmpdir)
            expected = "/usr/bin/docker run --rm -w {tmpdir}/dodo_tutorial/build/debug -i -t --volume={tmpdir}/dodo_tutorial/log:/var/log dodo_tutorial:1604 cmake -DCMAKE_INSTALL_PREFIX={tmpdir}/dodo_tutorial/install -DCMAKE_BUILD_TYPE=debug {tmpdir}/dodo_tutorial/src\n"  # noqa
            assert result == expected.format(tmpdir=str(tmpdir))
