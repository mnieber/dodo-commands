from funcy.py2 import rcompose, partial, remove, filter, map


def keep_if(f):
    return partial(filter, f)


def keep_truthy():
    return keep_if(bool)


def str_split_at(s, pos):
    return s[:pos], s[pos:]


def remove_if(f):
    return partial(remove, f)


def map_with(f):
    return partial(map, f)


def for_each(op):
    def f(seq):
        for x in seq:
            op(x)
        return seq

    return f


def pipe(x, *functions):
    return rcompose(*functions)(x)


def negate(f):
    return lambda x: not f(x)


def ds(f):
    return lambda x: f(*x)


def debug(x):
    print(x)
    __import__('pud' + 'b').set_trace()
    return x


def debug_as(f):
    return lambda x: debug(f(x))


def drill(x, *keys, default=None):
    result = x
    for key in keys:
        if not result or key not in result:
            return default
        result = result[key]
    return result


def map_to_tuple(f):
    def result(*args, **kwargs):
        return (f(*args, **kwargs), )

    return result
