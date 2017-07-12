

class Patch(object):
    """Describes patch applied to lines of code"""


class DeletePatch(Patch):
    """Cuts lines in range [start, end)"""

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __str__(self):
        if self.start + 1 == self.end:
            return 'Delete line #{}'.format(self.start + 1)
        else:
            return 'Delete lines #{} - #{}'.format(self.start + 1, self.end)


class InsertPatch(Patch):
    """Insert lines to given position"""

    def __init__(self, pos: int, lines: list):
        self.pos = pos
        self.lines = lines

    def __str__(self):
        piece = ''.join(self.lines)
        return 'Insert {!r} starting from line #{}'.format(piece, self.pos + 1)


class ReplacePatch(Patch):
    """Replaces lines in given range"""

    def __init__(self, start: int, end: int, lines: list):
        self.start = start
        self.end = end
        self.lines = lines

    def __str__(self):
        piece = ''.join(self.lines)

        if self.start + 1 == self.end:
            return 'Replace line #{} with {!r}'.format(self.start + 1, piece)
        else:
            return 'Replace lines #{} - #{} with {!r}'.format(self.start + 1, self.end, piece)


class StrPatch(object):
    """Describes patch applied to specific string"""


class StrDeletePatch(StrPatch):
    """Cuts chars in range [start, end)"""

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __str__(self):
        if self.start + 1 == self.end:
            return 'Delete char #{}'.format(self.start + 1)
        else:
            return 'Delete chars #{} - #{}'.format(self.start + 1, self.end)


class StrInsertPatch(StrPatch):
    """Insert chars to given position"""

    def __init__(self, pos: int, piece: str):
        self.pos = pos
        self.piece = piece

    def __str__(self):
        return 'Insert {!r} starting from position #{}'.format(self.piece, self.pos + 1)


class StrReplacePatch(StrPatch):
    """Replaces chars in given range"""

    def __init__(self, start: int, end: int, piece: str):
        self.start = start
        self.end = end
        self.piece = piece

    def __str__(self):
        if self.start + 1 == self.end:
            return 'Replace char #{} with {!r}'.format(self.start + 1, self.piece)
        else:
            return 'Replace chars #{} - #{} with {!r}'.format(self.start + 1, self.end, self.piece)


class LinePatch(Patch):
    """Describes patch applied to specific string"""

    def __init__(self, lineno: int, patches: list):
        self.lineno = lineno
        self.patches = patches

    def __str__(self):
        desc = '\n'.join(['\t- {}'.format(patch) for patch in self.patches])

        return 'With line #{} perform:\n{}\n'.format(self.lineno, desc)
