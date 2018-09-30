"""Tests for all standard commands."""
import os
import shutil
import ruamel.yaml


class TestConfigIO:  # noqa
    @classmethod
    def _load_config(cls, config_filename):
        with open(config_filename) as f:
            return ruamel.yaml.round_trip_load(f.read())

    @classmethod
    def _write_config(cls, config, config_filename):
        with open(config_filename, 'w') as f:
            f.write(ruamel.yaml.round_trip_dump(config))

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
        config['ROOT']['layers'] = []
        cls._write_config(config, config_filename)

    def test_commands(self):  # noqa
        from plumbum import local
        dodo_test_dir = os.path.expanduser('~/projects/dodo_test')
        global_dodo = local['dodo']
        skip_install = False

        if not skip_install:
            if os.path.exists(dodo_test_dir):
                shutil.rmtree(dodo_test_dir)
            global_dodo('activate', '--create', 'dodo_test')

        dodo = local[os.path.join(dodo_test_dir, 'dodo_commands/env/bin/dodo')]
        if not skip_install:
            dodo('bootstrap', 'src', 'extra/dodo_commands/res', '--force',
                 '--git-url',
                 'https://github.com/mnieber/dodo_commands_tutorial.git')

        config_filename = os.path.join(dodo_test_dir, 'dodo_commands', 'res',
                                       'config.yaml')
        res_dir = os.path.join(dodo_test_dir, 'dodo_commands', 'res')

        # dodo which
        assert "dodo_test" == dodo('which')[:-1]
        assert dodo_test_dir == dodo('which', 'project')[:-1]
        assert os.path.join(dodo_test_dir, 'src') == dodo('which', 'src')[:-1]
        assert res_dir == dodo('which', 'res')[:-1]
        assert config_filename == dodo('which', '--config')[:-1]
        assert 'debugger, docker, pause' == dodo('which', '--decorators')[:-1]

        # dodo cd
        assert "cd " + dodo_test_dir == dodo('cd')[:-1]

        # dodo check-version --config
        self._set_config_version(config_filename, '0.1.0')
        assert "Configuration needs update (0.1.0 < 1.0.0)" in dodo(
            'check-version', '--config')[:-1]
        self._set_config_version(config_filename, '1.0.0')
        assert "Configuration has not been commit to a local git" in dodo(
            'check-version', '--config')[:-1]

        # dodo check-version --dodo
        self._set_required_dodo_version(config_filename, '10000.0.0')
        assert "The dodo_commands package needs to be upgraded" in dodo(
            'check-version', '--dodo')[:-1]
        self._set_required_dodo_version(config_filename,
                                        dodo('--version')[:-1])
        assert "" == dodo('check-version', '--dodo')[:-1]

        # dodo diff
        result = dodo('diff', '.', '--echo').replace('\n', '')
        assert "diff %s/src/extra/dodo_commands/res %s/." % (dodo_test_dir,
                                                             res_dir) == result

        # dodo docker
        dodo('layer', 'docker', 'on')
        result = dodo('docker', '*', '--name', 'foo', '--echo').replace(
            '\n', '').replace('  \\', '').replace('  ', ' ')
        assert "docker run --name=foo --rm --interactive --tty --volume=%s/log:/var/log --workdir=/ dodo_tutorial:1604 /bin/bash" % dodo_test_dir == result

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
        assert self._load_config(config_filename)['ROOT']['layers'] == [
            'debug.on.yaml'
        ]
        dodo('layer', 'debug', 'off')
        assert self._load_config(config_filename)['ROOT']['layers'] == [
            'debug.off.yaml'
        ]

        # dodo new-command
        expected_new_command_file = os.path.join(
            dodo_test_dir, "src/extra/dodo_commands/dodo_tutorial_commands",
            "foo.py")
        if os.path.exists(expected_new_command_file):
            os.unlink(expected_new_command_file)
        dodo('new-command', 'foo', '--next-to', 'cmake')
        assert os.path.exists(expected_new_command_file)

        # dodo print-config
        assert "CMAKE_INSTALL_PREFIX: %s/install" % dodo_test_dir in dodo(
            "print-config")
