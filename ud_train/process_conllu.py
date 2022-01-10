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

def verify_projective(sentence : Sentence, node_id : str = None) -> List[str]:
    if node_id is None:
        roots = [tok.id for tok in sentence if tok.head == '0']
        if not roots: raise Exception('Sentence "%s" has no root' % sentence.text)
        if len(roots) > 1: raise Exception('Sentence "%s" has more than one root' % sentence.text)
        node_id = roots[0]
    child_ids = [tok.id for tok in sentence if tok.head == node_id]
    if not child_ids: # leaf node
        return [node_id]
    projection = [node_id]
    for child in child_ids:
        child_proj = verify_projective(sentence, child)
        if not child_proj: return []
        projection += child_proj
    projection.sort(key=lambda s : int(s))
    for i in range(1, len(projection)):
        if int(projection[i]) - int(projection[i-1]) != 1:
            print(projection[i-1], projection[i])
            return []
    return projection

