dodo commit-config
------------------

Breaking your local configuration can be serious problem, because it stops all Dodo Commands from working. Therefore, it's advisable to store your local configuration in a local git repository so that you can always restore a previous version. The ``dodo commit-config`` command makes this easy. It initializes a local git repository (if one doesn't exist already) next to your configuration files, and stages and commits all changes to the configuration.
