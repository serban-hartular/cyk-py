

sub_function_words = ['AdvSpec', 'AdvClit']
function_words = ['ADP', 'SCONJ', 'CCONJ', 'AUX', 'NUM', 'DET', 'PART']
content_words = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON']
multiword_heads = ['Prep', 'SConj', 'BARE_PP', 'CA_SI']
conjuncts = ['VPConj', 'NPConj', 'AdjPConj', 'AdvPConj', 'PPConj']

from cyk.parser import *
from cyk.rule_io import POSITION_STR, TYPE_STR


class UD_Node:
    deprel_dict = {'dobj':['obj', 'xcomp', 'ccomp'],
                   'subj':['nsubj', 'csubj', 'nsubj:pass'],
                   'iobj':['iobj'],
                   'ntmod':['nmod:tmod', 'obl'],
                   'predsup':['xcomp'],
                   'cpredobj':['xcomp'],
                   'obj2':['ccomp:pmod']
                   }
    def __init__(self, data : NodeData):
        self.data = data
        self.upos = str(self.data[TYPE_STR])
        self.id = str(str(self.data[POSITION_STR]))
        self.head = '-1'
        self.deprel = ''
        # self.position = data['position'].get()
        self.children : List[UD_Node] = []
    def traverse(self):
        yield self
        for child in self.children:
            for node in child.traverse():
                yield node
    def __str__(self):
        d = NodeData(self.data)
        d['head'] = self.head
        d[DEPREL_STR] = self.deprel
        return str(d)
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
    def differences(nodes : List['UD_Node'], conllu_nodes : list) -> tuple:
        # nodes.sort(key = lambda n : int(n.id))
        for node, conll in zip(nodes, conllu_nodes):
            if node.id != conll.id:
                print('Error! Different node ids for {}, {}'.format(str(node), conll.id))
                return (node, node.id, conll.id)
            if node.head != conll.head: # we may be doing partial trees, roots don't count
                return (node, node.head, conll.head)
            if node.deprel in UD_Node.deprel_dict and conll.deprel not in UD_Node.deprel_dict[node.deprel]:
                return (node, node.deprel, conll.deprel)
        return tuple() # ie, false
def are_function(ud_nodes : List[UD_Node]) -> bool:
    if len(ud_nodes) > 1:
        return True
    if ud_nodes[0].upos in (function_words + sub_function_words):
        return True
    return False

def to_ud(tree : Tree) -> List[UD_Node]:
    if not tree.children:
        return [UD_Node(tree.data)]
    if len(tree.children) == 1:
        if tree.type in sub_function_words:
            # print('sub funct')
            ud_node = UD_Node(tree.children[0].data)
            ud_node.upos = tree.type
            return [ud_node]
        return to_ud(tree.children[0])
    children = [to_ud(child) for child in tree.children]
    # if relation is fixed, fixed is child, make flat
    fixed = [f for f in tree.children_annot if f.get(DEPREL_STR) == 'fixed']
    if fixed:
        fixed = tree.children_annot.index(fixed[0])
        parent = 0 if fixed == 1 else 1
        fixed = children[fixed][0]
        fixed_kids = fixed.children
        fixed.children = []
        parent = children[parent][0]
        parent.children.extend([fixed] + fixed_kids)
        return [parent]
    if are_function(children[0]) and are_function(children[1]):
        # we have two function node trees, they will all be subordinate to one content word node
        # unless one is a sub_function word
        if children[0][0].upos in sub_function_words:
            parent = children[1][0]
            parent.children += children[0]
            return [parent]
        if children[1][0].upos in sub_function_words:
            parent = children[0][0]
            parent.children += children[1]
            return [parent]

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
        parent = children[1][0]
        parent.children += children[0]
        return [parent]
    # look for copulative or passive 'fi'
    if tree.type == 'VP' and (str(tree.data.get('cop')) == 'T' or str(tree.data.get('pass')) == 'T'):
        # look for 'fi'
        copula = [child for child in children if child[0].data[LEMMA_STR].get() == 'fi']
        if copula:
            # cop = 0 if str(tree.children[0].data[LEMMA_STR]) == 'fi' else 1
            cop = children.index(copula[0])
            main = 1 if cop == 0 else 0
            operator = children[cop][0]
            operator.deprel = 'cop' if (str(tree.data.get('cop'))) == 'T' else 'auxpass'
            # need to make copula/passive operator flat. all its children become children of parent
            operator_kids = operator.children
            operator.children = []
            parent = children[main][0]
            parent.deprel = tree.children_annot[main].get(DEPREL_STR) if tree.children_annot[main].get(DEPREL_STR) else ''
            # if parent is the npred or the pass, it's the head; otherwise, they are brothers 
            if parent.deprel in ['npred', 'pass']:
                parent.children.extend([operator] + operator_kids)
                parent.deprel = HEAD_STR
                return [parent]
            else:
                return [parent] + [operator] + operator_kids
        else: # look for npred or pass to use as head
            parent = [a[0] for a in children if a[0].deprel == HEAD_STR]
            if not parent: # pass them on up...
                raise Exception('no parent for npred/pass')
            parent = parent[0]
            for child in children:
                if child[0] != parent:
                    parent.children.extend(child)
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
        if LEMMA_STR not in child.data or LEMMA_STR not in tree.data:
            print(tree.data)
            print(child.data)
            exit(-1)
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
