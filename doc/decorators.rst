.. _decorators:

**********
Decorators
**********

A Decorator is a class that alters the workings of a Dodo Command script. It can extend or modify the arguments that are passed to ``Dodo.run``. For this purpose, the arguments for ``Dodo.run`` are constructed as a tree. Initially, this tree only has a root node that holds all arguments. Each decorator may restructure the argument tree by adding new tree nodes and changing existing nodes. The final list of arguments is obtained by flattening the tree in a pre-order fashion. This allows each decorator to prepend or append arguments, or completely rewrite the tree.


Prepending an argument
======================

The following example shows a decorator that prepends the arguments with the path to a debugger executable. The decorator should be placed in a ``decorators`` directory inside a commands directory:

.. code-block:: python

    # file: my_commands/decorators/debugger.py

    class Decorator:  # noqa
        def add_arguments(self, parser):  # noqa
            parser.add_argument(
                '--use-debugger',
                action='store_true',
                default=False,
                help="Run the command through the debugger"
            )

        def modify_args(self, dodo_args, root_node, cwd):  # noqa
            if not getattr(dodo_args, 'use_debugger', False):
                return root_node, cwd

            # Create a new root node with just the path to the debugger
            # Note that "debugger" is a name tag which is only used internally
            # to identify nodes in the tree.
            debugger_node = ArgsTreeNode(
                "debugger", args=[Dodo.get_config('/BUILD/debugger')]
            )

            # Since we want to make the debugger path a prefix, we add the
            # original arguments as a child node. When the tree is flattened
            # in a pre-order fashion, this will give the correct result.
            debugger_node.add_child(root_node)
            return debugger_node, cwd

Note that the decorator may also decide to return a different current working directory.

Appending an argument
=====================

This is similar to prepending, except that we do not need to create a new node

.. code-block:: python

    # file: my_commands/decorators/foo.py

    class Decorator:  # noqa
        def modify_args(self, dodo_args, root_node, cwd):  # noqa
            root_node.args.append('--foo')
            return root_node, cwd

Mapping decorators to commands
==============================

Not all decorators are compatible with all commands. For example, only some commands can be run inside a debugger. Therefore, the configuration contains a list of decorated command for each decorator. In this list, wildcards are allowed, and you can exclude commands by prefixing them with an exclamation mark:

.. code-block:: yaml

    ROOT:
      decorators:
        # Use a wildcard to decorate all commands, but exclude the foo command
        debugger: ['*', '!foo']
        # The cmake and runserver scripts can be run inside docker
        docker: ['cmake', 'runserver']

Printing arguments
==================

The structure of the argument tree determines how arguments are printed when the ``--echo`` or ``--confirm`` flag is used. The arguments in each node are indented in correspondence to the node's depth in the tree. The value of ``node.is_horizontal`` determines if arguments are printed horizontally or vertically. In the following example, the arguments in the root node (``docker run``) have a different indentation from the remaining arguments in the root's 4 child nodes. Moreover, since the ``rm``, ``interactive`` and ``tty`` flags are in a node for which ``is_horizontal=True``, they are printed on a single line:

.. code-block:: bash

    # assume cmake is decorated by the docker decorator in ${/ROOT/decorators}
    dodo cmake --echo

produces

.. code-block:: bash

    docker run  \
      --name=cmake  \
      --rm --interactive --tty  \
      dodo_tutorial:1604  \
      cmake -DCMAKE_BUILD_TYPE=release /home/maarten/projects/dodo_tutorial/src
