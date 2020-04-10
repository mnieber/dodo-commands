docker-exec --cmd
=================

To inspect a running docker container, run ``dodo docker-exec``.
This will print a list of running containers, allowing you to select one.


--cmd
-----

The command to run. Defaults to a shell giving you access to the container.


``$(/DOCKER/default_shell``
---------------------------

The shell to open when no ``--cmd`` is supplied in ``dodo docker-exec``.
