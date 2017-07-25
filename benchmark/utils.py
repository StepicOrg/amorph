from operator import truth
from re import search


def cut_data(df, status, limit=None):
    data = df[df.status == status].code.as_matrix()

    if isinstance(limit, float):
        limit = int(limit * len(data))

    if limit is None:
        limit = len(data)

    return data[:limit]


def format_lines(line, max_length):
    words = line.split()

    result = []
    accumulator = ''
    for idx, word in enumerate(words):
        if len(accumulator) + len(word) + bool(accumulator) <= max_length:
            accumulator += (' ' if accumulator else '') + word
        else:
            result.append(accumulator)
            accumulator = word
    result.append(accumulator)
    return '\n'.join(filter(truth, result))


def format_filename(title):
    return title.lower().replace(' ', '_')


def float_zeros_width(x):
    serialized = str(x)
    match = search('\.(0*)', serialized)

    if match is None or match.end(1) == len(serialized):
        return 0
    else:
        return len(match.group(1)) + 1
