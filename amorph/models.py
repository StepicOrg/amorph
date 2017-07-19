

class Patch(object):
    """Describes patch applied to code"""


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
    """Insert chars to given position"""

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
