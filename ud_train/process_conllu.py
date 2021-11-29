from typing import List

import pyconll
from pyconll.unit.sentence import Sentence
from pyconll.unit.token import Token

def elim_upos_from_conllu(sentence : Sentence, upos_to_purge : List[str]) -> List[Token]:
    # purge
    tok_list = [t for t in sentence if t.upos not in upos_to_purge]
    # change ids
    id_dict = {'0':'0'} # root stays the same
    for index, tok in enumerate(tok_list):
        old_id = tok.id
        tok.id = str(index + 1)
        id_dict[old_id] = tok.id
    # change ids in head entries
    for tok in tok_list:
        tok.head = id_dict[tok.head]
    return tok_list

