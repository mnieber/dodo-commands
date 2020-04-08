******************
Configuration file
******************

ROOT section
============

command_path (list)
-------------------

Search path for finding command scripts. The ``dodo_system_commands`` module is added to the command path by default.

command_path_exclude (filename pattern)
---------------------------------------

Exclude matching paths from the command path


LAYER_GROUPS section
====================

Contains a map from group-name to layer properties, e.g.

    .. code-block:: yaml

      LAYER:GROUPS:
        server:
        - reader:
            inferred_commands: [greet]
            name: rdr
            target_path: /foo/bar.yaml
        - writer: {}

