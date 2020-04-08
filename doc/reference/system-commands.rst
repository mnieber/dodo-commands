***************
System commands
***************

global-config
-------------

Used to change a setting in the global configuration, e.g. ``dodo global-config settings.diff_tool meld``

install-commands
----------------

Installs Python packages with command scripts into the global commands directory.

- ``--to-defaults``: adds the installed packages to the default commands directory.

- ``--make-default``: adds an already installed global commands package to the default commands directory

- ``--remove``: removes a package from the global commands directory

- ``--pip``: install commands from a pip package

- ``/path/to/package``: install a local Python package into the global commands directory

