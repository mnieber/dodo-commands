from dodo_commands.framework.global_config import load_global_config_parser


def get_aliases(config):
    result = list(config['ROOT'].get('aliases', {}).items())
    global_config = load_global_config_parser()
    if global_config.has_section('alias'):
        result.extend(global_config.items('alias'))
    return result


def find_alias(command_name, aliases):
    for key, val in aliases:
        if key == command_name:
            return val.split()
    return None
