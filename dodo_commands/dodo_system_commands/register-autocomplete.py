from dodo_commands.framework import Dodo


if Dodo.is_main(__name__, safe=True):
    print(
        'sudo register-python-argcomplete dodo > ' +
        '/etc/bash_completion.d/dodo_autocomplete.sh'
    )
