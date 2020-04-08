"""Tests for all standard commands."""
import os
import shutil
import sys

from dodo_commands.dependencies import (yaml_round_trip_dump,
                                        yaml_round_trip_load)


class TestConfigIO:  # noqa
    @classmethod
    def _load_config(cls, config_filename):
        with open(config_filename) as f:
            return yaml_round_trip_load(f.read())

    @classmethod
    def _write_config(cls, config, config_filename):
        with open(config_filename, 'w') as f:
            f.write(yaml_round_trip_dump(config))

    @classmethod
    def _set_config_version(cls, config_filename, version):
        config = cls._load_config(config_filename)
        config['ROOT']['version'] = version
        cls._write_config(config, config_filename)

    @classmethod
    def _set_required_dodo_version(cls, config_filename, version):
        config = cls._load_config(config_filename)
        config['ROOT']['required_dodo_commands_version'] = version
        cls._write_config(config, config_filename)

    @classmethod
    def _clear_layers(cls, config_filename):
        config = cls._load_config(config_filename)
        config['LAYERS'] = []
        cls._write_config(config, config_filename)

    def test_commands(self):  # noqa
        from dodo_commands.dependencies.get import plumbum
        local = plumbum.local

        dodo_test_dir = os.path.expanduser('~/projects/dodo_test')
        dodo_test_env_dir = os.path.expanduser(
            '~/.dodo_commands/envs/dodo_test')
        skip_install = False

        if not skip_install:
            if os.path.exists(dodo_test_dir):
                shutil.rmtree(dodo_test_dir)
            if os.path.exists(dodo_test_env_dir):
                shutil.rmtree(dodo_test_env_dir)

            from dodo_commands.dodo import main
            sys.argv = [
                'dodo', 'env', '--create', '--create-python-env', 'dodo_test'
            ]
            main()

        dodo = local[os.path.join(dodo_test_dir, '.env/bin/dodo')]
        if not skip_install:
            dodo('bootstrap', 'src', 'extra/dodo_commands/res', '--force',
                 '--git-url',
                 'https://github.com/mnieber/dodo_commands_tutorial.git')

        config_dir = os.path.join(dodo_test_dir, '.dodo_commands')
        config_filename = os.path.join(config_dir, 'config.yaml')

        # dodo which
        assert "dodo_test" == dodo('which')[:-1]
        assert dodo_test_dir == dodo('which', 'project')[:-1]
        assert os.path.join(dodo_test_dir, 'src') == dodo('which', 'src')[:-1]
        assert config_dir == dodo('which', 'res')[:-1]
        assert config_filename == dodo('which', '--config')[:-1]
        assert 'confirm, debugger, docker, pause' == dodo(
            'which', '--decorators')[:-1]

        # dodo cd
        assert "cd " + dodo_test_dir == dodo('cd')[:-1]

        # dodo check-version --config
        self._set_config_version(config_filename, '0.1.0')
        assert "Configuration needs update (0.1.0 < 1.0.0)" in dodo(
            'check-version', '--config')[:-1]
        self._set_config_version(config_filename, '1.0.0')

        # dodo check-version --dodo
        self._set_required_dodo_version(config_filename, '10000.0.0')
        assert "The dodo_commands package needs to be upgraded" in dodo(
            'check-version', '--dodo')[:-1]
        self._set_required_dodo_version(config_filename,
                                        dodo('--version')[:-1])
        assert "" == dodo('check-version', '--dodo')[:-1]

        # dodo diff
        result = dodo('diff', '.', '--echo').replace('\n', '')
        assert "diff %s/src/extra/dodo_commands/res %s/." % (
            dodo_test_dir, config_dir) == result

        # dodo docker
        dodo('layer', 'docker', 'on')
        result = dodo('docker', '*', '--name', 'foo',
                      '--echo').replace('\n',
                                        '').replace('  \\',
                                                    '').replace('  ', ' ')
        assert "docker run --name=foo --interactive --tty --rm --volume=%s/log:/var/log --workdir=/ dodo_tutorial:1604 /bin/bash" % dodo_test_dir == result

        # dodo docker-build
        result = dodo('docker-build', '--echo',
                      'base').replace('\n', '').replace('  \\', '')
        assert "docker build -t dodo_tutorial:1604 -f Dockerfile ." == result

        # dodo autostart
        autostart_file = os.path.expanduser('~/.dodo_commands_autostart')
        autostart_bak = autostart_file + '.bak'
        if os.path.exists(autostart_file):
            os.rename(autostart_file, autostart_bak)
        dodo('autostart', 'on')
        assert os.path.exists(autostart_file)
        dodo('autostart', 'off')
        assert not os.path.exists(autostart_file)
        if os.path.exists(autostart_bak):
            os.rename(autostart_bak, autostart_file)

        # dodo layer
        self._clear_layers(config_filename)
        dodo('layer', 'debug', 'on')
        assert self._load_config(config_filename)['LAYERS'] == [
            'debug.on.yaml'
        ]
        dodo('layer', 'debug', 'off')
        assert self._load_config(config_filename)['LAYERS'] == [
            'debug.off.yaml'
        ]

        # dodo print-config
        assert "CMAKE_INSTALL_PREFIX: %s/install" % dodo_test_dir in dodo(
            "print-config")

        # dodo drop-in
        tutorial_commands_dir = os.path.join(
            dodo_test_dir, "src/extra/dodo_commands/dodo_tutorial_commands")
        drop_in_dir = os.path.join(tutorial_commands_dir, "drop-in")
        os.mkdir(drop_in_dir)
        with open(os.path.join(drop_in_dir, "bar.txt"), "w") as ofs:
            ofs.write("bar")
        target_bar_path = os.path.join(config_dir, 'drops',
                                       'dodo_tutorial_commands', 'bar.txt')
        assert not os.path.exists(target_bar_path)
        dodo('drop-in', 'dodo_tutorial_commands')
        assert os.path.exists(target_bar_path)
