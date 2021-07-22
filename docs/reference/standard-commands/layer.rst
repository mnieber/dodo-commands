layer layer-group layer-value
=============================

Selects a layer from the chosen group and adds it to ``/LAYERS``. E.g. ``dodo layer server foo`` will add server.foo.yaml to ``LAYERS``.

.. note::

    Note that this makes a change to your main configuration file. Make sure that you do not have any unsaved configuration changes before calling this command.

Arguments:

- layer-group: selected group
- layer-value: selected layer within the selected layer-group
