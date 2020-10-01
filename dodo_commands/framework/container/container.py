import sys

from dodo_commands.framework.container import actions, facets
from dodo_commands.framework.container.facets import run
from dodo_commands.framework.paths import Paths


class Container:
    def _create_facets(self):
        self.paths = Paths()
        self.command_line = facets.CommandLine()
        self.layers = facets.init_layers(facets.Layers(), "config.yaml")
        self.config = facets.Config()
        self.commands = facets.init_commands(facets.Commands())

    def __init__(self):
        self._create_facets()

    @staticmethod
    def get(ctr):
        return ctr

    def run_actions(self):
        run(self, actions.command_line.parse_sys_argv)

        run(self, actions.layers.load_root_layer)
        run(self, actions.layers.load_named_layers)

        run(self, actions.commands.get_inferred_command_map)

        run(self, actions.command_line.get_expanded_layer_paths)
        run(self, actions.command_line.get_inferred_layer_paths)

        # Create the config
        run(self, actions.layers.select_layers)
        run(self, actions.config.check_conflicts_in_selected_layer_paths)
        run(self, actions.config.build_from_selected_layers)

        run(self, actions.commands.get_aliases_from_config)
        run(self, actions.commands.get_command_map)

        # This step may find out that the selected command alias
        # contains some --layer=foo.bar.yaml terms. These additional
        # layers are stored in self.command_line.more_given_layer_paths
        run(self, actions.command_line.expand_and_autocomplete_command_name)

        if self.command_line.more_given_layer_paths:
            run(self, actions.layers.select_layers)
            run(self, actions.config.build_from_selected_layers)

        if self.config.warnings:
            for warning in self.config.warnings:
                sys.stderr.write(warning)

