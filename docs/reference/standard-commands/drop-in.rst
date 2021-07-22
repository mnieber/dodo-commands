drop-in
=======

When you install a package with ``dodo install-commands`` it may contain more than just
command scripts. Some packages contain a so-called "drop-in" directory with configuration
files and other resources such as Dockerfiles. Since the Dodo Commands philosophy is that
you own your local configuration, the way to use these files is through copying them:

.. code-block:: bash

    dodo install-commands --pip dodo_deploy_commands
    # copy drop-in directory to ${/ROOT/res_dir}/drops/dodo_deploy_commands
    dodo drop-in dodo_deploy_commands

The ``dodo drop-in`` command copies the package's "drop-in" directory to
``${/ROOT/res_dir}/drops/<package_name>``. The default location of the ``drop-in`` source
directory is in the root of the package. Alternatively, the package root may contain a
``.drop-in`` file that holds the relative path to the actual ``drop-in`` directory.

You can use a copied configuration file by including it as a layer:

.. code-block:: bash

    # enable layer (drop.on.yaml)
    dodo layer drops/dodo_deploy_commands/drop on
    # disable layer (drop.off.yaml)
    dodo layer drops/dodo_deploy_commands/drop off
