from dodo_commands.framework import ramda as R
from dodo_commands.framework.command_error import CommandError
from dodo_commands.framework.layer_metadata import LayerMetadata


def get_metadata_by_layer_name(root_layer):
    result = {}

    groups = R.path_or({}, "LAYER_GROUPS")(root_layer)
    for group_name, group in groups.items():
        for group_item in group:
            if isinstance(group_item, str):
                layer_name = group_item
                target_path = None
            elif isinstance(group_item, dict):
                layer_name, metadata = list(group_item.items())[0]
                metadata = metadata or {}
                target_path = metadata.get("target_path")
                if not target_path:
                    raise CommandError(
                        "Missing target_path for layer %s in group %s"
                        % (layer_name, group_name)
                    )
            else:
                raise CommandError(
                    "Invalid layer group item: %s. Must be a string or a dict"
                    % group_item
                )

            layer_metadata = LayerMetadata(target_path, group_name)

            if layer_name in result:
                prev_layer_metadata = result[layer_name]
                raise CommandError(
                    "Name conlict for layer '%s' in groups '%s' and '%s'"
                    % (
                        layer_name,
                        prev_layer_metadata.group_name,
                        layer_metadata.group_name,
                    )
                )

            result[layer_name] = layer_metadata

    return result
