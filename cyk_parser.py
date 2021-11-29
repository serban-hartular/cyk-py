import math

from rule import Rule, NodeData, DEPREL_STR, HEAD_STR
from rule_io import TYPE_STR, FORM_STR, LEMMA_STR
from typing import List, Dict, Tuple

class Grammar:
    def __init__(self, rules : List[Rule]):
        self.rules = rules
        self.singletons = [r for r in rules if len(r.children) == 1]
        self.doubletons = [r for r in rules if len(r.children) == 2]
        others = [r for r in rules if len(r.children) != 1 and len(r.children) != 2]
        if others:
            raise Exception("Rules can only have 1 or 2 children: '%s'" % others[0].to_text())
        self.nonterminals = set([rule.parent.constraints[TYPE_STR].values.get() for rule in self.rules])
        self.terminals = set([ruleitem.constraints[TYPE_STR].values.get() for rule in rules \
                              for ruleitem in ([rule.parent] + rule.children) \
                              if ruleitem.constraints[TYPE_STR].values.get() not in self.nonterminals])
        self.assign_scores()
    def assign_scores(self):
        for nonterm in self.nonterminals:
            rules = [rule for rule in self.rules if rule.parent.constraints[TYPE_STR].values.get() == nonterm]
            n = 0
            for rule in rules:
                if len(rule.children) == 1: # this is kind of doubtful
                    rule.score = 1.00001
                    continue
                rule.score = 1 / (n+1)
                n += 1
    def is_known(self, type_str : str) -> bool:
        return type_str in self.terminals.union(self.nonterminals)
class Tree:
    def __init__(self, data : NodeData, rule : Rule = None, children : List['Tree'] = None, children_annot : List[Dict] = None, guess = False):
        self.data = data
        self.children = children if children else list()
        self.children_annot = children_annot
        self.rule = rule
        self.score = 1
        self.num_nodes = 1 + sum([child.num_nodes for child in self.children])
        self.nscore = 0
        self.guess = guess
        if not children:
            self.form = ' '.join([s for s in data[FORM_STR]]) if FORM_STR in data else ''
        else:
            self.form = ' '.join([c.form for c in self.children])
        self.type = self.data[TYPE_STR].get() if TYPE_STR in self.data.keys() else '?'
        self.assign_score()

    def assign_score(self):
        self.score = self.rule.score if self.rule else 1
        for child in self.children:
            self.score *= child.score
        self.nscore = math.log10(self.score) / self.num_nodes
        
    def to_jsonable(self, add_children = False) -> dict:
        str_attrs = ['type', 'form', 'score', 'nscore', 'rule', 'guess']
        obj = {k:str(self.__getattribute__(k)) for k in str_attrs}
        obj['data'] = self.data.to_jsonable()
        if add_children:
            obj['children'] = [child.to_jsonable(add_children) for child in self.children]
        obj['children_annot'] = self.children_annot
        return obj
    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()
    def is_similar(self, other : 'Tree') -> bool:
        # if not self.children and not other.children:
        #     return self.data == other.data
        # if self.type != other.type or self.data.get(LEMMA_STR) != other.data.get(LEMMA_STR):
        #     return False
        head1, arglist1 = self.get_args()
        head2, arglist2 = other.get_args()
        return head1 == head2 and set(arglist1) == set(arglist2)
        # return set(self.get_args()) == set(other.get_args())
    def get_head_child(self) -> 'Tree':
        if not self.children: return None
        # head deprel
        for annot, child in zip(self.children_annot, self.children):
            if annot.get(DEPREL_STR) == HEAD_STR:
                return child
        # same lemma
        heads = [c for c in self.children if c.data.get(LEMMA_STR) == self.data.get(LEMMA_STR)]
        if heads:
            return heads[0]
        # return first child
        return self.children[0]
    def get_args(self) -> ('Tree', List[tuple]):
        """ Returns the children attached to the tree and the rules they were attached by
        for nodes of the same type with the same lemma beneath this tree
        """
        node = self
        arglist = []
        while True:
            next = node.get_head_child()
            if not next: break
            others = [c for c in node.children if c != next]
            if others:
                arglist += [(child, node.rule) for child in others]
            else: # this was a singleton rule
                arglist.append((None, node.rule))
            node = next
        return node, arglist # head, arglist
    def __str__(self):
        if len(self.children) < 2:
            text = '"' + self.form + '"'
        else:
            text = '"' + self.children[0].form + '|' + self.children[1].form + '"'
        text += self.data[TYPE_STR].get() if TYPE_STR in self.data.keys() else ''
        other_keys = [k for k in self.data.keys() if k not in [FORM_STR, TYPE_STR]]
        if other_keys:
            text += '('
            text += ' '.join([k + '=' + ','.join(self.data[k]) for k in other_keys])
            text += ')'
        return text
    def __repr__(self):
        return str(self)
    def detail(self, recurse = False, depth = 0) -> str:
        text = '\t' * depth + str(self) + '\n'
        if not recurse:
            text += '\t' * depth + str(self.rule) + '\n'
        for child in self.children:
            if not recurse:
                text += '\t' * (depth+1) + str(child) + '\n'
            elif len(child.children) == 1 and not child.children[0].children:
                text += '\t' * (depth+1) + str(child) + ' <- ' + str(child.children[0]) + '\n'
            else:
                text += child.detail(recurse, depth+1)
        return text
    def detail2(self, depth=0, newline = False) -> str:
        if newline:
            text = '\n' + (' ' * depth) + '('
        else:
            text = '('
        text += ((self.type if self.type else '?') + ' ' + (str(self.data.get(FORM_STR)) if self.data.get(FORM_STR) else '')) 
        if len(self.children) > 0:
            text += self.children[0].detail2(depth+1, False)
        if len(self.children) > 1:
            text += self.children[1].detail2(depth+1, True)
        text += ')'
        return text


class ParseSquare(List[Tree]):
    def __init__(self, tree_list : List[Tree] = list()):
        super().__init__(tree_list)
    def contains_similar(self, t : Tree) -> bool:
        for c in self:
            if c.is_similar(t):
                return True
        return False
    def add(self, trees, exclude_similar = False) -> int:
        if not hasattr(trees, '__iter__'):
            trees = [trees]
        if exclude_similar:
            trees = [t for t in trees if not self.contains_similar(t)]
        self.extend(trees)
        return len(trees)
        
class Parser:
    def __init__(self, grammar : Grammar):
        self.grammar = grammar
        self.table = list()
    def parse(self, input : List[ParseSquare], exclude_similar = True):
        N = len(input)
        self.generate_table(N)
        for sq in input: # verify input -- no cell empty
            if not sq: raise Exception('Empty input cell')
        self.table[0] = [sq for sq in input] # initialize bottom row
        for row_index in range(0, len(self.table)):
            for col_index in range(0, len(self.table[row_index])):
                square = self.table[row_index][col_index]
                self.do_doubleton_rules(row_index, col_index, exclude_similar)
                self.do_singleton_rules(square, exclude_similar)
                square.sort(key=lambda t: -t.nscore)
        return self.table
    def generate_table(self, N : int):
        self.table = list() # array that holds the rows        
        for row_index in range(0, N): # create row
            row = [ParseSquare() for col in range(row_index, N)]
            self.table.append(row)
    def do_singleton_rules(self, square : ParseSquare, exclude_similar : bool):
        i = 0 # index of node in square
        while(i < len(square)):
            node = square[i]
            for rule in self.grammar.singletons:
                (data, annotations) = rule.apply([node.data])
                if not data: continue
                new_node = Tree(data, rule, [node], annotations)
                # similar = [t for t in square if new_node.is_similar(t)]
                # if not exclude_similar or (exclude_similar and not similar):
                #     square.append(new_node)
                square.add(new_node, exclude_similar)
            i += 1
    @staticmethod
    def generate_child_squares(row_index : int, col_index : int) -> List[tuple]:
        return [((s, col_index),(row_index-s-1, col_index+s+1)) for s in range(0, row_index)]
    def do_doubleton_rules(self, row_index : int, col_index : int, exclude_similar : bool):
        square = self.table[row_index][col_index]
        for ((r1, c1), (r2, c2)) in Parser.generate_child_squares(row_index, col_index):
            child_sq1 = self.table[r1][c1]
            child_sq2 = self.table[r2][c2]
            for node1, node2 in [(n1, n2) for n1 in child_sq1 for n2 in child_sq2]: 
                for rule in self.grammar.doubletons:
                    (data, annotations) = rule.apply([node1.data, node2.data])
                    if not data: continue # rule could not be applied
                    new_node = Tree(data, rule, [node1, node2], annotations)
                    # similar = [t for t in square if new_node.is_similar(t)] # list of trees similar to new_node
                    # if not exclude_similar or (exclude_similar and not similar): # to ommit if similar
                    #     square.append(new_node)
                    square.add(new_node, exclude_similar)
    def root(self, **kwargs):
        return self.cell((len(self.table)-1, 0), **kwargs)
    def cell(self, pos, y = None, **kwargs) -> ParseSquare:
        """kwargs:  filter='all' will return all content
                    filter='guess' will return only guesses
                    filter=None will return only non-guesses (default)
                    filter=lambda t will run filter on content before returning
        """
        if y is not None:
            pos = (pos, y)
        filter = kwargs.get('filter')
        if filter == 'all': filter=lambda t : True
        if filter == 'guess' : filter=lambda t : t.guess
        if filter is None : filter = lambda t : not t.guess
        return ParseSquare([t for t in self.table[pos[0]][pos[1]] if filter(t)])
    
    def get_parses(self, position : tuple = None, no_kids = True) -> List[List[Tree]]:
        """ The no_kids flag means children residing in the same square won't be returned.
        This dramatically reduces the number of incomplete parses. (Another consequence of 
        allowing singleton rules.)
        """
        (row, col) = position if position else (len(self.table)-1, 0)
        if self.cell(row, col): # done!
            all_children = [child for node in self.cell(row, col) for child in node.children]
            return [[p] for p in self.cell(row, col) if p not in all_children]
        # try children positions
        parses = []
        for possible_children in Parser.generate_child_squares(row, col):
            (childpos1, childpos2) = possible_children
            parses1 = self.get_parses(childpos1)
            parses2 = self.get_parses(childpos2)
            for child1 in parses1:
                for child2 in parses2:
                    parses.append(child1 + child2)
        parses.sort(key=lambda n : len(n))
        return parses
    def to_jsonable(self):
        tree_list = []
        N = len(self.table)
        json_table = list()  # array that holds the rows        
        for row_index in range(0, N):  # create row
            row = [list() for col in range(row_index, len(self.table))]
            json_table.append(row)
            for col_index in range(0, len(row)):
                for tree in self.cell((row_index, col_index), filter='all'): #self.table[row_index][col_index]:
                    json_table[row_index][col_index].append(len(tree_list)) #this will be the tree ID
                    tree_list.append(tree)  # tree ID is index of tree in list
        tree_json_list = []
        for i in range(0, len(tree_list)):
            tree_json = tree_list[i].to_jsonable()
            tree_json['id'] = i
            # debug
            # tree_json['children'] = [tree_list.index(child) for child in tree_list[i].children]
            tree_json['children'] = list()
            for child in tree_list[i].children:
                try:
                    tree_json['children'].append(tree_list.index(child))
                except Exception as e:
                    print('Parent:' + str(tree_list[i]))
                    print('Child:' + str(child))
                    raise e
            tree_json_list.append(tree_json)
        # get actual parses
        parses = self.get_parses()
        root_list = []
        first_len = 0
        first_score = 0
        for parse in parses: # only those that aren't too long
            roots = tuple([tree_list.index(i) for i in parse])
            score = sum([p.nscore for p in parse])
            if first_len == 0:
                first_len = len(roots)
                first_score = score
            if len(roots) > first_len and score < first_score:
                break
            if roots not in root_list:
                root_list.append(roots)

        # get guessed parses, if any
        guess_list = self.cell((N-1, 0), filter='guess')
        guess_list = [tree_list.index(t) for t in guess_list]
        return {'nodes':tree_json_list, 'table':json_table, 'root_list':root_list, 
                'guess_list': guess_list}
            
