dial number
===========

Selects directory from the list in ``/DIAL`` and prints it as a ``cd`` command to the console, e.g.

.. code-block:: yaml

    DIAL:
    - ${/ROOT/src_dir}/backend
    - ${/ROOT/src_dir}/frontend


.. code-block:: bash

    # prints "cd /path/to/backend/"
    dodo dial 0

    # change to backend directory
    dodo dial 0 | source


This becomes useful when combines with a key binding in the shell, e.g. in Fish the following binding allows you to go to a directory with F1 and F2.

.. code-block:: bash

    # /.config/fish/functions/dial.fish
    function dial
        dodo dial $argv | source
        commandline -f repaint
    end

    # /.config/fish/functions/fish_user_key_bindings.fish
    function fish_user_key_bindings
        bind --key f1 "dial 0"
        bind --key f2 "dial 1"
    end⏎

number
------

The number to dial.
