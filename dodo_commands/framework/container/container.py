from dodo_commands.framework.container import actions, facets
from dodo_commands.framework.paths import Paths


class Container:
    def _create_facets(self):
        self.paths = Paths()
        self.command_line = facets.init_command_line(facets.CommandLine())
        self.layers = facets.init_layers(facets.Layers(), 'config.yaml')
        self.config = facets.Config()
        self.commands = facets.init_commands(facets.Commands())

    def __init__(self):
        self._create_facets()

    def run_actions(self):
        actions.layers.action_load_root_layer(self)
        actions.layers.action_load_named_layers(self)

        actions.commands.action_get_inferred_command_map(self)

        actions.command_line.action_get_expanded_layer_paths(self)
        actions.command_line.action_get_inferred_layer_paths(self)

        # Create the config
        actions.layers.action_select_layers(self)
        actions.config.action_check_conflicts_in_selected_layer_paths(self)
        actions.config.action_build_from_selected_layers(self)

        actions.commands.action_get_aliases_from_config(self)
        actions.commands.action_get_command_map(self)

        # This step may find out that the selected command alias
        # contains some --layer=foo.bar.yaml terms. These additional
        # layers are stored in self.command_line.more_given_layer_paths
        actions.command_line.action_expand_and_autocomplete_command_name(self)

        if self.command_line.more_given_layer_paths:
            actions.layers.action_select_layers(self)
            actions.config.action_build_from_selected_layers(self)
