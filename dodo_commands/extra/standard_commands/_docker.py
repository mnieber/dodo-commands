import re


def _filter_choices(all_choices, raw_choice):
    regexp = r"(\d)+(\-(\d)+)?,?"
    result = []
    span = [None, None]
    for choice in [x for x in re.finditer(regexp, raw_choice)]:
        if span[0] is None:
            span[0] = choice.span()[0]
        if span[1] is None or span[1] == choice.span()[0]:
            span[1] = choice.span()[1]
        from_index = int(choice.group(1)) - 1
        to_index = int(choice.group(3)) - 1 if choice.group(3) else from_index
        for idx in range(from_index, to_index + 1):
            result.append(all_choices[idx])
    return result, span
