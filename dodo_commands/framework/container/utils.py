from dodo_commands.framework import ramda as R


# if there are two args that equal "--" then we assume that everything
# behind the second instance of "--" is a part of the "left side" of the
# command line
def rearrange_double_dash(args):
    left, rest = R.split_when(R.equals("--"), args)
    middle, right = [], []
    if rest:
        middle, rest = R.split_when(R.equals("--"), rest[1:])
        if rest:
            right, rest = R.split_when(R.equals("--"), rest[1:])
    return left + right + (R.prepend("--")(middle) if middle else [])
