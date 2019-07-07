from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import (symlink, query_yes_no,
                                          is_using_system_dodo, exe_exists)
from dodo_commands.framework.config import Paths, CommandError
import platform
import os
import shutil
from six.moves import input as raw_input
# import tempfile

# Since we'd like the user to install meld, we require it here. If it's not found
# then it will be installed via the meta file (setup.meta).
from plumbum.cmd import meld  # noqa


def _args():
    parser = ArgumentParser(
        description='Set up Dodo Commands after installation')

    # Parse the arguments.
    # Optionally, use `config_args` to include additional arguments whose values
    # come either from the configuration file or from the command line (see docs).
    args = Dodo.parse_args(parser)
    return args


def _install_commands(pip_package, confirm):
    if confirm or query_yes_no('Install package %s ' % pip_package +
                               'into the default commands directory'):
        Dodo.run(['dodo', 'install-commands', '--pip', pip_package])


def _create_left_file(left_dir, filename, contents):
    left_filename = os.path.join(left_dir, filename)
    with open(left_filename, 'w') as ofs:
        ofs.write(contents)
    return left_filename


def _create_right_file(right_dir, filename, source_path):
    right_filename = os.path.join(right_dir, filename)
    if os.path.exists(source_path):
        symlink(source_path, right_filename)
    return right_filename


bash_profile = """
# Only in case you've install Dodo Commands in a virtual env: uncomment this line
# and set the path to the directory that holds the system dodo executable.
#
# export PATH=$PATH:/path/to/virtual/env/bin

# Load the .dodo_commands_autostart file
if [ -f ~/.dodo_commands_autostart ]; then
    . ~/.dodo_commands_autostart
fi

# Add a short-cut for $(dodo <command_name>). It let's you use sdodo <command_name>.
sdodo() {
    $(dodo $@)
}
"""

global_config = """[alias]
wh = which
pc = print-config
ec = edit-config
dk = docker-kill
de = docker-exec
dc = docker-commit
ac = activate
acc = activate --create
mr = menu --run
mm = menu
"""

meld_instructions = """
The setup command will now assist you in comparing your configuration files
to the prototypical ones by comparing files in meld.
Just copy the changes that you agree with from the files on the left side
to the files on the right side.
"""

no_meld_instructions = """
Since meld is not installed, the setup command will not assist you directly
in comparing your configuration files to the prototypical ones. However, you
can do this manually by comparing %s to %s.
Press any key when you are done with the manual comparison, so setup will
continue to remove these temporary directories.
"""

# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    if not is_using_system_dodo():
        raise CommandError(
            "Please deactivate your dodo project first by running 'deactivate'."
        )

    if not args.confirm:
        if query_yes_no(
                'Turn on confirmation for each command that setup executes?'):
            os.environ['__DODO_UNIVERSAL_CONFIRM__'] = '1'

    is_darwin = platform.system() == 'Darwin'
    is_linux = platform.system() == 'Linux'

    if exe_exists('meld'):
        Dodo.run(['dodo', 'global-config', 'settings.diff_tool', 'meld'])

    Dodo.run(['dodo', 'autostart', 'on'])

    for pip_package in ('dodo_webdev_commands', 'dodo_git_commands'):
        _install_commands(pip_package, args.confirm)

    # tmp_dir = tempfile.mkdtemp()
    tmp_dir = '/tmp/dodo_setup'
    shutil.rmtree(tmp_dir)  # HACK

    left_dir = os.path.join(tmp_dir, 'left')
    if not os.path.exists(left_dir):
        os.makedirs(left_dir)
    right_dir = os.path.join(tmp_dir, 'right')
    if not os.path.exists(right_dir):
        os.makedirs(right_dir)

    names = dict(bash_profile='.bash_profile' if is_darwin else '.bashrc')

    _create_left_file(left_dir, names['bash_profile'], bash_profile)
    bash_profile_path = os.path.join(os.path.expanduser('~'),
                                     names['bash_profile'])
    if not os.path.exists(bash_profile_path):
        print('The bash profile file %s does not exist.' % bash_profile_path)
        if query_yes_no('Create it?'):
            Dodo.run(['touch', bash_profile_path])
    _create_right_file(right_dir, names['bash_profile'], bash_profile_path)

    _create_left_file(left_dir, 'config', global_config)
    _create_right_file(right_dir, 'config', Paths().global_config_filename())

    if not exe_exists('meld'):
        print(no_meld_instructions % (left_dir, right_dir))
        raw_input()
    else:
        print(meld_instructions)
        Dodo.run(['meld', left_dir, right_dir])

    shutil.rmtree(tmp_dir)
