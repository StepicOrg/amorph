from difflib import SequenceMatcher
from amorph.models import DeletePatch, InsertPatch, ReplacePatch


class Index(object):
    def __init__(self, text):
        self.lines = text.splitlines(keepends=True)
        self.lens = [len(line) for line in self.lines]

    def map(self, line, char):
        return sum(self.lens[:line]) + char

    def line_start(self, line):
        return self.map(line, 0)

    def line_end(self, line):
        return self.map(line, self.lens[line])

    def subtext(self, line_start, line_end):
        return ''.join(self.lines[line_start:line_end])

    def __getitem__(self, key):
        return self.lines[key]

    def __len__(self):
        return len(self.lines)


class DiffPatcher(object):
    """Computes set of patches to transform one text into another using diff"""

    """Min similarity ratio of two strings to be matched"""
    CUTOFF = 0.75

    def __init__(self,
                 is_line_junk=None,
                 is_char_junk=None):
        """
        Inits patcher based on diff
        :param is_line_junk: Single string argument function that \
                             returns True if line should be ignored
        :param is_char_junk: Single string argument function that \
                             returns True if character should be ignored
        """
        self.is_line_junk = is_line_junk
        self.is_char_junk = is_char_junk

    def get_patches(self, source: Index, target: Index):
        """
        Returns list of patches for transforming text a to text b
        :param source: Lines of source string to transform
        :param target: Lines of target string for transformation
        :return: List of patches
        """
        cruncher = SequenceMatcher(self.is_line_junk, source, target)
        for tag, start1, end1, start2, end2 in cruncher.get_opcodes():
            if tag == 'replace':
                yield from self._replace_with_matches(source, (start1, end1), target, (start2, end2))

            elif tag == 'delete':
                yield DeletePatch(source.line_start(start1), source.line_end(end1-1))

            elif tag == 'insert':
                yield InsertPatch(source.line_start(start1), target.subtext(start2, end2))

    def _replace_with_matches(self,
                              source: Index,
                              source_bounds: tuple,
                              target: Index,
                              target_bounds: tuple):
        """
        Tries to match similar strings and compute inner patches of matches \
        or fails with plain lines changes
        :param source: Line slice of source string
        :param source_bounds: Tuple of indices source slice was taken from in format [start, end)
        :param target: Line slice of target string
        :param target_bounds: Tuple of indices target slice was taken from in format [start, end)
        :return: List of patches
        """
        src_start, src_end = source_bounds
        tgt_start, tgt_end = target_bounds

        # matcher for finding similarities between pairs
        cruncher = SequenceMatcher(self.is_char_junk)

        # first pair of equal strings if any
        src_equal, tgt_equal = None, None

        # pair of best matching strings and their ratio
        best_ratio, src_best, tgt_best = self.CUTOFF - 0.01, None, None

        # search for best matching pair in source and target texts
        for j in range(tgt_start, tgt_end):
            tgt_current = target[j]

            for i in range(src_start, src_end):
                src_current = source[i]

                if src_current == tgt_current:
                    if src_equal is None:
                        src_equal, tgt_equal = i, j
                    continue

                cruncher.set_seq1(src_current)
                cruncher.set_seq2(tgt_current)

                # ratio function can be slow so should be
                # executed only if upper bounds are satisfactory
                if cruncher.real_quick_ratio() > best_ratio and \
                      cruncher.quick_ratio() > best_ratio and \
                      cruncher.ratio() > best_ratio:
                    best_ratio, src_best, tgt_best = cruncher.ratio(), i, j

        if best_ratio < self.CUTOFF:
            if src_equal is None:
                # no close matches or equal strings, plain replace
                yield ReplacePatch(source.line_start(src_start),
                                   source.line_end(src_end-1),
                                   target.subtext(tgt_start, tgt_end))
                return
            # no close matches but identical strings found
            best_ratio, src_best, tgt_best = 1.0, src_equal, tgt_equal
        else:
            # there is close match, not interested in equal strings if any
            src_equal, best_equal = None, None

        # dump patches before synch point
        yield from self._replace_auto(source, (src_start, src_best), target, (tgt_start, tgt_best))

        # dump patches for two best matched strings
        src_close, tgt_close = source[src_best], target[tgt_best]
        if src_equal is None:
            cruncher.set_seqs(src_close, tgt_close)
            for tag, start1, end1, start2, end2 in cruncher.get_opcodes():
                if tag == 'replace':
                    yield ReplacePatch(source.map(src_best, start1),
                                       source.map(src_best, end1),
                                       tgt_close[start2:end2])

                elif tag == 'delete':
                    yield DeletePatch(source.map(src_best, start1),
                                      source.map(src_best, end1))

                elif tag == 'insert':
                    yield InsertPatch(source.map(src_best, start1),
                                      tgt_close[start2:end2])

        # dump patches after synch point
        yield from self._replace_auto(source, (src_best + 1, src_end), target, (tgt_best + 1, tgt_end))

    def _replace_auto(self,
                      source: Index,
                      source_bounds: tuple,
                      target: Index,
                      target_bounds: tuple):
        """
        Chooses type of patch to apply judging by indices bounds given
        :param source: Line slice of source string
        :param source_bounds: Tuple of indices source slice was taken from in format [start, end)
        :param target: Line slice of target string
        :param target_bounds: Tuple of indices target slice was taken from in format [start, end)
        :return: List of patches
        """
        src_start, src_end = source_bounds
        tgt_start, tgt_end = target_bounds

        if src_start < src_end:
            if tgt_start < tgt_end:
                yield from self._replace_with_matches(source, (src_start, src_end), target, (tgt_start, tgt_end))
            else:
                yield DeletePatch(source.line_start(src_start), source.line_end(src_end-1))
        elif tgt_start < tgt_end:
            yield InsertPatch(source.line_start(src_start), target.subtext(tgt_start, tgt_end))


def get_patches(source: str,
                target: str,
                is_line_junk=None,
                is_char_junk=None):
    """
    Returns list of patches for transforming one code to another
    :param source: Source code to transform
    :param target: Target code for transformation
    :param is_line_junk: Single string argument function that \
                         returns True if line should be ignored
    :param is_char_junk: Single string argument function that \
                         returns True if character should be ignored
    :return: List of patches
    """
    d = DiffPatcher(is_line_junk, is_char_junk)
    yield from d.get_patches(Index(source), Index(target))
