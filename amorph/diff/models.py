from typing import List


class Patch(object):
    """Describes patch applied to lines of code"""


class DeletePatch(Patch):
    """Cuts lines in range [start, end)"""

    def __init__(self, start: int, end: int):
        self.start: int = start
        self.end: int = end

    def __str__(self):
        if self.start + 1 == self.end:
            return f'Delete line #{self.start + 1}'
        else:
            return f'Delete lines #{self.start + 1} - #{self.end}'


class InsertPatch(Patch):
    """Insert lines to given position"""

    def __init__(self, pos: int, lines: List[str]):
        self.pos: int = pos
        self.lines: List[str] = lines

    def __str__(self):
        piece = ''.join(self.lines)
        return f'Insert {repr(piece)} starting from line #{self.pos + 1}'


class ReplacePatch(Patch):
    """Replaces lines in given range"""

    def __init__(self, start: int, end: int, lines: List[str]):
        self.start: int = start
        self.end: int = end
        self.lines: List[str] = lines

    def __str__(self):
        piece = ''.join(self.lines)

        if self.start + 1 == self.end:
            return f'Replace line #{self.start + 1} with {repr(piece)}'
        else:
            return f'Replace lines #{self.start + 1} - #{self.end} with {repr(piece)}'


class StrPatch(object):
    """Describes patch applied to specific string"""


class StrDeletePatch(StrPatch):
    """Cuts chars in range [start, end)"""

    def __init__(self, start: int, end: int):
        self.start: int = start
        self.end: int = end

    def __str__(self):
        if self.start + 1 == self.end:
            return f'Delete char #{self.start + 1}'
        else:
            return f'Delete chars #{self.start + 1} - #{self.end}'


class StrInsertPatch(StrPatch):
    """Insert chars to given position"""

    def __init__(self, pos: int, piece: str):
        self.pos: int = pos
        self.piece: str = piece

    def __str__(self):
        return f'Insert {repr(self.piece)} starting from position #{self.pos + 1}'


class StrReplacePatch(StrPatch):
    """Replaces chars in given range"""

    def __init__(self, start: int, end: int, piece: str):
        self.start: int = start
        self.end: int = end
        self.piece: str = piece

    def __str__(self):
        if self.start + 1 == self.end:
            return f'Replace char #{self.start + 1} with {repr(self.piece)}'
        else:
            return f'Replace chars #{self.start + 1} - #{self.end} with {repr(self.piece)}'


class LinePatch(Patch):
    """Describes patch applied to specific string"""

    def __init__(self, lineno: int, patches: List[StrPatch]):
        self.lineno: int = lineno
        self.patches: List[StrPatch] = patches

    def __str__(self):
        desc = '\n'.join([f'\t- {patch}' for patch in self.patches])

        return f'With line #{self.lineno} perform:\n{desc}\n'
