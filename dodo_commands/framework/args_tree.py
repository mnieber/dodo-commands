class ArgsTreeNode:
    def __init__(self, name, args=None, is_horizontal=True):
        self.name = name
        self.children = []
        # this flag controls if nodes are printed horizontally
        self.is_horizontal = is_horizontal
        self.args = args or []

    def add_child(self, node):
        self.children.append(node)
        return node

    def __getitem__(self, name):  # noqa
        return next(x for x in self.children if x.name == name)

    def get(self, name, default_value):
        values = [x for x in self.children if x.name == name]
        return next(values) if values else default_value

    def has_child(self, name):  # noqa
        return len([x for x in self.children if x.name == name])

    def append(self, x):  # noqa
        self.args.append(x)

    def extend(self, x):  # noqa
        self.args.extend(x)

    def flatten(self):
        result = list(self.args)
        for x in self.children:
            result.extend(x.flatten())
        return result

    def to_str(self, indent=0, slash=False):
        terminal = "  \\\n" if slash else "\n"

        if self.is_horizontal:
            if self.args:
                result = indent * " " + " ".join(self.args) + terminal
            else:
                result = ""
        else:
            result = ""
            for x in self.args:
                result += indent * " " + x + terminal
        for child in self.children:
            last_root_child = indent == 0 and child == self.children[-1]
            result += child.to_str(
                indent=indent + 2, slash=slash and not last_root_child)
        return result
