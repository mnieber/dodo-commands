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
                base_name = layer_name
                inferred_commands = []
                target_path = None
            elif isinstance(group_item, dict):
                layer_name, metadata = list(group_item.items())[0]
                metadata = metadata or {}
                inferred_commands = list(metadata.get("inferred_by", []))
                target_path = metadata.get("target_path")
                base_name = metadata.get("base_name", layer_name)

            target_path = target_path or "%s.%s.yaml" % (group_name, base_name)
            layer_metadata = LayerMetadata(target_path, inferred_commands, group_name)

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
