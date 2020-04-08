dodo env [--init/--create/--forget] --create-python-env [--latest <name>]
-------------------------------------------------------------------------

This command returns a string that - when sourced - activates the <name> environment.

Arguments:

- --create: create a new project directory in the global projects directory. Also creates a new Dodo Commands environment in the global environments directory.

- --init: creates a new Dodo Commands environment in the global environments directory. The current directory is taken as the project directory in this environment.

- --forget: removes <name> from the global environments directory

- --latest: activate the latest used environment

- <name>: name of the environment. If ``-`` is used then the previously used environment is activated.
