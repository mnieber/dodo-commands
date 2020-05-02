dial [--group=default] number
=============================

Selects directory from a list in ``/DIAL`` and prints it to the console, e.g.

.. code-block:: yaml

    DIAL:
      default:
        # used for cd'ing into a directory
        '1': ${/ROOT/src_dir}/backend
        '2': ${/ROOT/src_dir}/frontend
      shift:
        # used as a short-cut for using a Dodo Commands layer
        '1': dodo backend.
        '2': dodo frontend.


.. code-block:: bash

    # prints "/path/to/backend/"
    dodo dial 1

    # cd's into "/path/to/backend/"
    cd $(dodo dial 1)


This becomes useful when combined with a key binding in the shell. For example, in Fish the following binding allows you to go to a directory (in the ``${/DIAL/default}`` group) with F1 and F2, and insert a string (in the ``${/DIAL/shift}`` group) with Shift+F1 and Shift+F2, allowing for a very fast work-flow:

.. code-block:: bash

    # /.config/fish/functions/dial_cd.fish
    function dial_cd
        cd (dodo dial $argv)
        commandline -f repaint
    end

    # /.config/fish/functions/dial_insert.fish
    function dial_insert
        cd (dodo dial $argv)
        commandline -f repaint
    end

    # /.config/fish/functions/fish_user_key_bindings.fish
    function fish_user_key_bindings
        bind --key f1 "dial_cd 0"
        bind --key f2 "dial_cd 1"

        bind \e\[1\;2P "dial_insert 1"
        bind \e\[1\;2Q "dial_insert 2"
    end⏎


group[=default]
---------------

The group inside ``${/DIAL}`` from which to pick.

The number to dial.


number
------

The number to dial.