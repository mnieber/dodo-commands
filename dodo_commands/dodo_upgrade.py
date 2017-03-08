import os
import sys
from plumbum import local


def main():  # noqa
    pip = local[os.path.join(os.path.dirname(sys.executable), "pip")]
    pip("install", "--upgrade", "dodo_commands")
