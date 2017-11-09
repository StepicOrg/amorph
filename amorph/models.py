import abc


class Patch(abc.ABC):
    """Describes patch applied to code"""

    @abc.abstractmethod
    def to_dict(self):
        pass

    @property
    @abc.abstractmethod
    def size(self):
        pass

    @staticmethod
    def from_dict(raw):
        if raw['type'] == 'delete':
            return DeletePatch(raw['start'], raw['stop'])

        elif raw['type'] == 'insert':
            return InsertPatch(raw['pos'], raw['text'])

        elif raw['type'] == 'update':
            return ReplacePatch(raw['start'], raw['stop'], raw['text'])

    @abc.abstractmethod
    def __str__(self):
        pass


class DeletePatch(Patch):
    """Cuts chars in range [start, stop)"""

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def to_dict(self):
        return {
            'type': 'delete',
            'start': self.start,
            'stop': self.stop
        }

    @property
    def size(self):
        return self.stop - self.start

    def __str__(self):
        if self.start + 1 == self.stop:
            return 'Delete char #{}'.format(self.start)
        else:
            return 'Delete chars #{} - #{}'.format(self.start, self.stop - 1)


class InsertPatch(Patch):
    """
    Insert chars to given position

    WARNING: this patch means "insert string before character in position `pos`"
             so if `pos == len(source_string)` it means that `text` should be
             appstoped to the stop of `source_string`
    """

    def __init__(self, pos: int, text: str):
        self.pos = pos
        self.text = text

    def to_dict(self):
        return {
            'type': 'insert',
            'pos': self.pos,
            'text': self.text
        }

    @property
    def size(self):
        return len(self.text)

    def __str__(self):
        return 'Insert {!r} starting from position #{}'.format(self.text, self.pos)


class ReplacePatch(Patch):
    """Replaces chars in given range"""

    def __init__(self, start: int, stop: int, text: str):
        self.start = start
        self.stop = stop
        self.text = text

    def to_dict(self):
        return {
            'type': 'replace',
            'start': self.start,
            'stop': self.stop,
            'text': self.text
        }

    @property
    def size(self):
        return self.stop - self.start + len(self.text)

    def __str__(self):
        if self.start + 1 == self.stop:
            return 'Replace char #{} with {!r}'.format(self.start, self.text)
        else:
            return 'Replace chars #{} - #{} with {!r}'.format(self.start, self.stop - 1, self.text)
