import re

from dodo_commands.dependencies.get import parsimonious, six

raw_input = six.moves.input
ParseError = parsimonious.exceptions.ParseError
Grammar = parsimonious.grammar.Grammar
NodeVisitor = parsimonious.nodes.NodeVisitor


def parse_choice(raw_choice):
    grammar = Grammar(
        r"""
      choices   = (term "," choices) / term
      term       = double / single
      single     = number ""
      double     = first "-" last
      first      = number ""
      last       = number ""
      number     = ~r"[\d]+"
      """
    )

    def remove_whitespace(x):
        pattern = re.compile(r"\s+")
        return re.sub(pattern, "", x)

    class Visitor(NodeVisitor):
        def __init__(self):
            self.choices = []

        def visit_single(self, node, visited_children):
            choice = int(node.text)
            self.choices.append((choice, choice))

        def visit_first(self, node, visited_children):
            choice = int(node.text)
            self.choices.append((choice, None))

        def visit_last(self, node, visited_children):
            choice = int(node.text)
            self.choices[-1] = (self.choices[-1][0], choice)

        def generic_visit(self, node, visited_children):
            return visited_children or node

    tree = grammar.parse(remove_whitespace(raw_choice))
    visitor = Visitor()
    visitor.visit(tree)

    idxs = []
    for from_index, to_index in visitor.choices:
        for idx in range(from_index, to_index + 1):
            idxs.append(idx)
    return idxs


class ChoicePicker:
    def __init__(self, choices, start_index=1, allow_free_text=False, labels=None):
        self._choices = choices
        self._labels = labels
        self._start_index = start_index
        self.allow_free_text = allow_free_text
        self.free_text = None

    def print_choices(self):
        raise NotImplementedError()

    def question(self):
        raise NotImplementedError()

    def on_invalid_index(self, index):
        pass

    def pick(self):
        self.free_text = None
        self.idxs = []
        self.print_choices(self._labels or self._choices)
        while True:
            raw_choice = raw_input(self.question())
            try:
                self.idxs = parse_choice(raw_choice)
            except ParseError:
                if self.allow_free_text:
                    self.free_text = raw_choice
                    return
                print("Sorry, I did not understand that")
            else:
                for idx in self.idxs:
                    idx0 = idx - self._start_index
                    if (idx0 < 0) or (idx0 >= len(self._choices)):
                        self.on_invalid_index(idx)
                return

    def get_choices(self):
        return [self._choices[x] for x in self.get_idxs0()]

    def get_idxs0(self):
        return [x - self._start_index for x in self.idxs]
