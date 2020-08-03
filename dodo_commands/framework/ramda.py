from dodo_commands.dependencies.get import funcy


def filter(f):
    return funcy.partial(funcy.filter, f)


def remove_if(f):
    return filter(complement(f))


def split(pos):
    def f(s):
        return s[:pos], s[pos:]

    return f


def map(f):
    return funcy.partial(funcy.map, f)


def for_each(op):
    def f(seq):
        for x in seq:
            op(x)
        return seq

    return f


def pipe(*functions):
    return lambda x: funcy.rcompose(*functions)(x)


def ds(f):
    return lambda x: f(*x)


def debug(x):
    print(x)
    __import__("pud" + "b").set_trace()
    return x


def debug_as(f):
    return lambda x: debug(f(x))


def path(*keys):
    def f(x):
        result = x
        for key in keys:
            if not result or key not in result:
                raise Exception("Key not found %s" % key)
            result = result[key]
        return result

    return f


def path_or(default, *keys):
    def f(x):
        result = x
        for key in keys:
            if not result or key not in result:
                return default
            result = result[key]
        return result

    return f


def when(pred, transform):
    def f(x):
        return transform(x) if pred(x) else x

    return f


def prepend(x):
    def f(collection):
        return [x, *collection]

    return f


def equals(x):
    def f(y):
        return y == x

    return f


def split_when(pred, collection):
    return funcy.split_by(complement(pred), collection)


complement = funcy.complement
concat = funcy.concat
cut_prefix = funcy.cut_prefix
cut_suffix = funcy.cut_suffix
uniq = funcy.distinct
flatten = funcy.flatten
merge = funcy.merge
always = funcy.constantly
tap = funcy.tap
