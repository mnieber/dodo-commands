import os

from dodo_commands import Dodo


def _args():
    Dodo.parser.description = "Restart the docker service"
    args = Dodo.parse_args()
    return args


# Use safe=False if the script makes changes other than through Dodo.run
if Dodo.is_main(__name__, safe=True):
    args = _args()
    memo = os.environ.get("__DODO_UNIVERSAL_CONFIRM__")
    os.environ["__DODO_UNIVERSAL_CONFIRM__"] = "1"
    Dodo.run(["sudo", "service", "docker", "stop"])
    if memo is None:
        del os.environ["__DODO_UNIVERSAL_CONFIRM__"]
    else:
        os.environ["__DODO_UNIVERSAL_CONFIRM__"] = memo
    Dodo.run(["sudo", "service", "docker", "restart"])
