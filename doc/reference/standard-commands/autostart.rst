autostart [on off]
==================

Writes (or removes) a small shell script in ``~/.config/fish/conf.d`` and
``~/.config/bash/conf.d``. When this small script is sourced, it activates the last
used environment. In Bash, this requires that you add these lines to the `~/.bashrc`` file:

.. code-block:: bash

    if [ -f ~/.config/bash/conf.d/dodo_autostart ]; then
        . ~/.config/bash/conf.d/dodo_autostart
    fi
