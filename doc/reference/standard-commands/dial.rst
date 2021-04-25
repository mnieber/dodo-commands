.. _dial:

dial [--group=default] number
=============================

Selects directory from a list in ``/DIAL`` and prints it to the console, e.g.

.. code-block:: yaml

    DIAL:
      default:
        # used as a short-cut for using a Dodo Commands layer
        '1': dodo backend.
        '2': dodo frontend.
      shift:
        # used for cd'ing into a directory
        '1': ${/ROOT/src_dir}/backend
        '2': ${/ROOT/src_dir}/frontend


.. code-block:: bash

    # prints "/path/to/backend/"
    dodo dial 1

    # cd's into "/path/to/backend/"
    cd $(dodo dial --group=shift 1)


This becomes useful when combined with a key binding in the shell. For example, in Fish the following binding allows you to go to a directory (in the ``${/DIAL/default}`` group) with F1 and F2, and insert a string (in the ``${/DIAL/shift}`` group) with Shift+F1 and Shift+F2, allowing for a very fast work-flow:

.. code-block:: bash

    # /.config/fish/functions/dial_insert.fish
    function dial_insert
        set cmd (dodo dial -g default $argv)
        if test $cmd
            commandline -i $cmd
        end
    end

    # /.config/fish/functions/dial_cd.fish
    function dial_cd
        cd (dodo dial $argv)
        commandline -f repaint
    end

    # /.config/fish/functions/fish_user_key_bindings.fish
    function fish_user_key_bindings
        bind --key f1 "dial_insert 0"
        bind --key f2 "dial_insert 1"

        bind \e\[1\;2P "dial_cd 1"
        bind \e\[1\;2Q "dial_cd 2"
    end⏎

.. tip::

   Dodo Commands comes with "dial" key bindings for fish. You can find them as follows:

   .. code-block:: bash

     # find location of the which.py script, e.g.
     dodo which --fish-config

     # There you will find subdirectories called ``functions`` and ``conf.d`` that need
     # to be copied to ~/.config/fish (merging them with the existing directories there)
     # If ~/.config/fish does not yet these subdirectories then you can do this using:
     cd (dodo which --fish-config)
     cp -rf functions conf.d ~/.config/fish


group[=default]
---------------

The group inside ``${/DIAL}`` from which to pick.

The number to dial.


number
------

The number to dial.