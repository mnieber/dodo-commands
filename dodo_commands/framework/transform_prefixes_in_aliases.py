from dodo_commands.framework.get_aliases import get_aliases


def transform_prefixes_in_aliases(config, metadata_by_layer_name):
    aliases = get_aliases(config["ROOT"])
    for name, value in list(aliases.items()):
        parts = value.split()
        for idx, part in list(enumerate(parts)):
            if part.startswith("--"):
                continue

            prefixes = part.split(".")
            parts[idx] = prefixes.pop()

            for prefix in prefixes:
                layer = (
                    metadata_by_layer_name[prefix].target_path
                    if prefix in metadata_by_layer_name
                    else prefix
                )
                parts.append("--layer=%s" % layer)

            aliases[name] = " ".join(parts)
            break
