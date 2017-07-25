

class Patch(object):
    """Describes patch applied to code"""

    def __str__(self):
        raise NotImplementedError

    def to_dict(self):
        result = {'type': type(self).__name__}
        result.update(self.__dict__)
        return result


class DeletePatch(Patch):
    """Cuts chars in range [start, end)"""

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __str__(self):
        if self.start + 1 == self.end:
            return 'Delete char #{}'.format(self.start)
        else:
            return 'Delete chars #{} - #{}'.format(self.start, self.end - 1)


class InsertPatch(Patch):
    """
    Insert chars to given position

    WARNING: this patch means "insert string before character in position `pos`"
             so if `pos == len(source_string)` it means that `piece` should be
             appended to the end of `source_string`
    """

    def __init__(self, pos: int, piece: str):
        self.pos = pos
        self.piece = piece

    def __str__(self):
        return 'Insert {!r} starting from position #{}'.format(self.piece, self.pos)


class ReplacePatch(Patch):
    """Replaces chars in given range"""

    def __init__(self, start: int, end: int, piece: str):
        self.start = start
        self.end = end
        self.piece = piece

    def __str__(self):
        if self.start + 1 == self.end:
            return 'Replace char #{} with {!r}'.format(self.start, self.piece)
        else:
            return 'Replace chars #{} - #{} with {!r}'.format(self.start, self.end - 1, self.piece)
