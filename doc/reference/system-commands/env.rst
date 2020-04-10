env [--init/--create/--forget] --create-python-env [--latest <name>]
====================================================================

This command returns a string that - when sourced - activates the <name> environment.

Arguments:

--create
--------

Creates a new project directory in the global projects directory.
Also creates a new Dodo Commands environment in the global environments directory.

--init
------

Creates a new Dodo Commands environment in the global environments directory.
The current directory is taken as the project directory in this environment.

--forget
--------

Removes <name> from the global environments directory

--latest
--------

Activates the latest used environment

<name>
------

Name of the environment. If ``-`` is used then the previously used environment is activated.
