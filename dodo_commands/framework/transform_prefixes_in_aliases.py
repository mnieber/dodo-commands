def transform_prefixes_in_aliases(config, layer_props_by_layer_name):
    aliases = config["ROOT"].get("aliases", {})
    for name, value in list(aliases.items()):
        parts = value.split()
        for idx, part in list(enumerate(parts)):
            if part.startswith("--"):
                continue

            prefixes = part.split(".")
            parts[idx] = prefixes.pop()

            for prefix in prefixes:
                layer = (layer_props_by_layer_name[prefix].target_path
                         if prefix in layer_props_by_layer_name else prefix)
                parts.append("--layer=%s" % layer)

            aliases[name] = " ".join(parts)
            break
