import token
import tokenize
from difflib import SequenceMatcher

from asttokens import ASTTokens
from asttokens.util import Token

from amorph.models import DeletePatch, InsertPatch, ReplacePatch


class ComparableToken(Token):
    def __eq__(self, other):
        return hash(self) == hash(other)

    def _key(self):
        return self.type, self.string

    def __hash__(self):
        return hash(self._key())

    def __str__(self):
        return '[{}] -> {!r}'.format(tokenize.tok_name[self.type], self.string)

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_token(tok):
        return ComparableToken(
            type=tok.type,
            string=tok.string,
            start=tok.start,
            end=tok.end,
            line=tok.line,
            index=tok.index,
            startpos=tok.startpos,
            endpos=tok.endpos
        )


def get_tokens(source):
    tokens = ASTTokens(source).tokens
    cmp_tokens = map(ComparableToken.from_token, tokens)
    return list(filter(not_junk, cmp_tokens))


def is_junk(tok):
    return tok.type in [token.ENDMARKER, token.NEWLINE, token.DEDENT,
                        tokenize.COMMENT, tokenize.NL, tokenize.ENCODING]


def not_junk(tok):
    return not is_junk(tok)


def get_patches(source: str, target: str):
    src_tokens = get_tokens(source)
    src_len = len(src_tokens)
    tgt_tokens = get_tokens(target)

    cruncher = SequenceMatcher(None, src_tokens, tgt_tokens)
    for type, start1, end1, start2, end2 in cruncher.get_opcodes():
        if type == 'equal':
            continue

        # append to the end case. see warning in InsertPatch definition
        if start1 == src_len:
            src_start = src_tokens[start1-1].endpos
        else:
            src_start = src_tokens[start1].startpos

        if type != 'insert':
            src_end = src_tokens[end1-1].endpos

        if type != 'delete':
            tgt_start = tgt_tokens[start2].startpos
            tgt_end = tgt_tokens[end2-1].endpos

        if type == 'delete':
            yield DeletePatch(src_start, src_end)
        elif type == 'insert':
            yield InsertPatch(src_start, target[tgt_start:tgt_end])
        elif type == 'replace':
            yield ReplacePatch(src_start, src_end, target[tgt_start:tgt_end])
