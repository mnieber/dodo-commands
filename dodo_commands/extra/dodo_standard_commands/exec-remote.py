import os
import sys

from dodo_commands import Dodo
from dodo_commands.framework.command_map import execute_script, get_command_map
from dodo_commands.framework.command_path import get_command_dirs


def _args():
    Dodo.parser.description = "Download a command script and run it"

    Dodo.parser.add_argument("url")
    Dodo.parser.add_argument("script_args")

    args = Dodo.parse_args()
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    tmp_dir = os.path.join(os.path.expanduser("~"), ".dodo_commands", "tmp")
    package_dir = os.path.join(tmp_dir, "exec_scripts")

    if ".commands.yaml" in args.url:
        last_slash = args.url.rfind("/")
        url = args.url[:last_slash]
        cmd_name = args.url[last_slash + 1 :]
    else:
        url = args.url
        cmd_name = os.path.splitext(os.path.basename(url))[0]

    Dodo.run(["mkdir", "-p", package_dir])
    Dodo.run(["touch", os.path.join(package_dir, "__init__.py")])
    Dodo.run(["wget", url, "-O", os.path.join(package_dir, os.path.basename(url))])

    command_map = get_command_map(get_command_dirs([package_dir], []))
    sys.argv = sys.argv[1:]
    execute_script(command_map, cmd_name)
