import sys

from dodo_commands.framework.container import facets
from dodo_commands.framework.container.actions.command_line import (
    expand_and_autocomplete_command_name,
    get_layer_paths_from_command_prefix,
    parse_input_args,
)
from dodo_commands.framework.container.actions.commands import (
    get_aliases_from_config,
    get_command_map,
)
from dodo_commands.framework.container.actions.config import (
    build_from_selected_layers,
    check_conflicts_in_selected_layer_paths,
)
from dodo_commands.framework.container.actions.layers import (
    get_metadata_by_layer_name,
    load_named_layers,
    load_root_layer,
    select_layers,
)
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
        load_root_layer(self)
        get_metadata_by_layer_name(self)
        load_named_layers(self)
        parse_input_args(self)

        while True:
            get_layer_paths_from_command_prefix(self)

            # Create the config
            select_layers(self)
            check_conflicts_in_selected_layer_paths(self)
            build_from_selected_layers(self)

            get_aliases_from_config(self)
            get_command_map(self)

            if not expand_and_autocomplete_command_name(self):
                break

        if self.config.warnings:
            for warning in self.config.warnings:
                sys.stderr.write(warning)
