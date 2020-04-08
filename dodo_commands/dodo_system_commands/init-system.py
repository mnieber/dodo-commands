import os
import subprocess
import sys


def _packages_dirname():
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     "../dependencies/packages"))


packages_dirname = _packages_dirname()
if not os.path.exists(packages_dirname):
    os.makedirs(packages_dirname)

for dependency in [
        'python-dotenv==0.12.0',
        'plumbum==1.6.8',
        'ruamel.yaml==0.16.10',
        'parsimonious==0.8.1',
        'six==1.14.0',
        'funcy==1.14',
        'ansimarkup==1.4.0',
        'argcomplete==1.11.1',
        'semantic_version==2.8.4',
]:
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--target',
            packages_dirname, dependency
        ])
    except:  # noqa
        pass
