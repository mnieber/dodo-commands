.. _decorators:

**********
Decorators
**********

A Decorator is a class that alters the workings of a Dodo Command script by extending or modifying the arguments that are passed to ``Dodo.run``. For this purpose, the arguments for ``Dodo.run`` are constructed as a tree. Initially, this tree only has a root node that holds all arguments. Each decorator may restructure the argument tree by adding new tree nodes and changing existing nodes. The final list of arguments is obtained by flattening the tree in a pre-order fashion. This allows each decorator to prepend or append arguments, or completely rewrite the tree.


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

Note that the decorator returns both the new argument tree and a current working directory. This means that it's possible to change the current working directory for the decorated command as well.

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

The structure of the argument tree determines how arguments are printed when the ``--echo`` or ``--confirm`` flag is used. We've seen above that nodes in the tree are created with the ``ArgsTreeNode`` constructor. The arguments in this node are indented in correspondence to the node's depth in the tree. The ``ArgsTreeNode`` constructor takes an optional argument ``is_horizontal`` that determines if arguments are printed horizontally or vertically, e.g.


.. code-block:: python

    docker_node = ArgsTreeNode("docker", args=['docker', 'run'])
    tty_node = ArgsTreeNode(
        ["tty", args=['--rm', '--interactive', '--tty'],
        is_horizontal=True
    )
    docker_node.add_child(tty_node)

    # add more nodes to the tree...

.. code-block:: bash

    # assume cmake is decorated with the docker decorator
    dodo cmake --echo

produces

.. code-block:: bash

    docker run  \
      --rm --interactive --tty  \
      --name=cmake  \
      dodo_tutorial:1604  \
      cmake -DCMAKE_BUILD_TYPE=release /home/maarten/projects/dodo_tutorial/src
