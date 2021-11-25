

function_words = ['ADP', 'SCONJ', 'CCONJ', 'AUX', 'NUM', 'DET', 'PART']
content_words = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON']
multiword_heads = ['Prep', 'SConj', 'BARE_PP', 'CA_SI']
conjuncts = ['VPConj', 'NPConj', 'AdjPConj', 'AdvPConj', 'PPConj']

from cyk_parser import *

class UD_Node:
    def __init__(self, data : NodeData):
        self.data = data
        self.children : List[UD_Node] = []
    def upos(self):
        return self.data[TYPE_STR].get()

def are_function(ud_nodes : List[UD_Node]) -> bool:
    if len(ud_nodes) > 1:
        return True
    if ud_nodes[0].upos() in function_words:
        return True
    return False

def to_ud(tree : Tree) -> List[UD_Node]:
    if not tree.children:
        return [UD_Node(tree.data)]
    if len(tree.children) == 1:
        return to_ud(tree.children[0])
    children = [to_ud(child) for child in tree.children]
    if are_function(children[0]) and are_function(children[1]):
        return children[0] + children[1]
    if are_function(children[0]) and not are_function(children[1]):
        assert len(children[1]) == 1
        parent = children[1][0]
        parent.children += children[0]
        return [parent]
    if not are_function(children[0]) and are_function(children[1]):
        assert len(children[0]) == 1
        parent = children[0][0]
        parent.children += children[1]
        return [parent]
    # we have two content nodes.
    for annot, i in zip(tree.children_annot, range(0, len(tree.children_annot))):
        if annot.get(DEPREL_STR) == HEAD_STR:
            # this is the head
            o = 0 if i == 1 else 1
            parent = children[i][0]
            parent.children += children[o]
            return [parent]
