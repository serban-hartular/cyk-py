

function_words = ['ADP', 'SCONJ', 'CCONJ', 'AUX', 'NUM', 'DET', 'PART']
content_words = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON']
multiword_heads = ['Prep', 'SConj', 'BARE_PP', 'CA_SI']
conjuncts = ['VPConj', 'NPConj', 'AdjPConj', 'AdvPConj', 'PPConj']

from cyk_parser import *
from rule_io import POSITION_STR, TYPE_STR, FORM_STR

class UD_Node:
    def __init__(self, data : NodeData):
        self.data = data
        self.upos = str(self.data[TYPE_STR])
        self.id = str(str(self.data[POSITION_STR]))
        self.head = '-1'
        self.deprel = ''
        self.children : List[UD_Node] = []
    def traverse(self):
        yield self
        for child in self.children:
            for node in child.traverse():
                yield node
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return str(self)
    def set_heads(self, head='0'):
        self.head = head
        for child in self.children:
            child.set_heads(self.id)
    @staticmethod
    def token_list(node : 'UD_Node') -> List['UD_Node']:
        node.set_heads()
        nodes = [n for n in node.traverse()]
        nodes.sort(key=lambda n : int(n.id))
        return nodes
    @staticmethod
    def differences(nodes : List['UD_Node'], conllu_nodes : list()) -> tuple:
        for node, conll in zip(nodes, conllu_nodes):
            if node.id != conll.id:
                print('Error! Different node ids for {}, {}'.format(str(node), str(conll)))
                return (node, node.id, conll.id)
            if node.head != conll.head:
                return (node, node.head, conll.head)
        return []
def are_function(ud_nodes : List[UD_Node]) -> bool:
    if len(ud_nodes) > 1:
        return True
    if ud_nodes[0].upos in function_words:
        return True
    return False

def to_ud(tree : Tree) -> List[UD_Node]:
    if not tree.children:
        return [UD_Node(tree.data)]
    if len(tree.children) == 1:
        return to_ud(tree.children[0])
    children = [to_ud(child) for child in tree.children]
    if are_function(children[0]) and are_function(children[1]):
        # we have two function node trees, they will all be subordinate to one content word node
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
    # if it's a RP (relative phrase), the verb is the head in UD
    if tree.type == 'RP':
        print('RP')
        parent = children[1][0]
        parent.children += children[0]
        return [parent]
    # look for copulative or passive 'fi'
    if tree.type == 'VP' and (str(tree.data.get('cop')) == 'T' or str(tree.data.get('pass')) == 'T'):
        deprel = 'cop' if (str(tree.data.get('cop'))) == 'T' else 'aux:pass'
        # look for 'fi'
        cop = 0 if str(tree.children[0].data[LEMMA_STR]) == 'fi' else 1
        main = 1 if cop == 0 else 0
        parent = children[main][0]
        operator = children[cop][0]
        operator.deprel = deprel
        # need to make copula/passive operator flat. all its children become children of parent
        operator_kids = operator.children
        operator.children = []
        parent.children.extend([operator] + operator_kids)
        return [parent]
    # look for head
    for annot, i in zip(tree.children_annot, range(0, len(tree.children_annot))):
        if annot.get(DEPREL_STR) == HEAD_STR:
            # this is the head
            o = 0 if i == 1 else 1
            parent = children[i][0]
            # set deprel of child, if it exists
            deprel = tree.children_annot[o][DEPREL_STR] if DEPREL_STR in tree.children_annot[o] else ''
            children[o][0].deprel = deprel
            parent.children += children[o]
            return [parent]
    # look for one with same lemma
    for child, i in zip(tree.children, range(0, len(tree.children))):
        if child.data[LEMMA_STR].get() == tree.data[LEMMA_STR].get():
            # this is the head
            o = 0 if i == 1 else 1
            parent = children[i][0]
            parent.children += children[o]
            return [parent]
    # I'm out of ideas, pick the first one
    parent = children[0][0]
    parent.children += children[1]
    return [parent]
