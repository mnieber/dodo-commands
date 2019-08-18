from importlib import import_module
import fnmatch
import os

from dodo_commands.framework.command_path import get_command_path


def uses_decorator(config, command_name, decorator_name):
    patterns = (config.get('ROOT', {}).get('decorators',
                                           {}).get(decorator_name, []))
    approved = [
        pattern for pattern in patterns if not pattern.startswith("!")
        and fnmatch.filter([command_name], pattern)
    ]
    rejected = [
        pattern for pattern in patterns if pattern.startswith("!")
        and fnmatch.filter([command_name], pattern[1:])
    ]
    return len(approved) and not len(rejected)


def get_decorators(command_name, config):
    result = []
    # should be returned as the last item in the list
    confirm_decorator = None
    for name, directory in _all_decorators(config).items():
        decorator = _load_decorator(name, directory)
        if decorator.is_used(config, command_name, name):
            if name == 'confirm':
                confirm_decorator = decorator
            else:
                result.append(decorator)

    if confirm_decorator:
        result.append(confirm_decorator)

    return result


def _load_decorator(name, directory):
    """Load and return decorator class in module with given name."""
    return import_module(directory + "." + name).Decorator()


def _all_decorators(config):
    """Returns a mapping from decorator name to its directory."""
    command_path = get_command_path(config)
    command_path.extend_sys_path()
    result = {}
    for item in command_path.items:
        try:
            module_path = os.path.basename(item) + ".decorators"
            module = import_module(module_path)
            for decorator in os.listdir(module.__path__[0]):
                name, ext = os.path.splitext(decorator)
                if ext == '.py' and name != '__init__':
                    result[name] = module_path
        except ImportError:
            continue
    return result
