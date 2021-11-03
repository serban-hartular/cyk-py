
from rule import Rule, NodeData
from rule_io import TYPE_STR, FORM_STR, LEMMA_STR
from typing import List, Dict, Tuple


# FORM_STR = rule.FORM_STR

class Grammar:
    def __init__(self, rules : List[Rule]):
        self.rules = rules
        self.singletons = [r for r in rules if len(r.children) == 1]
        self.doubletons = [r for r in rules if len(r.children) == 2]
        others = [r for r in rules if len(r.children) != 1 and len(r.children) != 2]
        if others:
            raise Exception("Rules can only have 1 or 2 children: '%s'" % others[0].to_text())
        self.nonterminals = set([rule.parent[TYPE_STR].values.get() for rule in self.rules])
        self.terminals = set([ruleitem[TYPE_STR].values.get() for rule in rules \
                              for ruleitem in ([rule.parent] + rule.children) \
                              if ruleitem[TYPE_STR].values.get() not in self.nonterminals])
        self.assign_scores()
    def assign_scores(self):
        for nonterm in self.nonterminals:
            rules = [rule for rule in self.rules if rule.parent[TYPE_STR].values.get() == nonterm]
            for n in range(0, len(rules)):
                rules[n].score = 1 / (n+1)

class Tree:
    def __init__(self, data : NodeData, rule : Rule = None, children : List['Tree'] = None, children_annot : List[Dict] = None):
        self.data = data
        self.children = children if children else list()
        self.children_annot = children_annot
        self.rule = rule
        self.score = 1
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
    def to_jsonable(self, add_children = False) -> dict:
        str_attrs = ['type', 'form', 'score', 'rule']
        obj = {k:str(self.__getattribute__(k)) for k in str_attrs}
        obj['data'] = self.data.to_jsonable()
        if add_children:
            obj['children'] = [child.to_jsonable(add_children) for child in self.children]
        return obj
    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()
    def is_similar(self, other : 'Tree') -> bool:
        return set(self.get_args()) == set(other.get_args())
    def get_head_child(self) -> 'Tree':
        """Find child of same type and same lemma"""
        heads = [c for c in self.children if c.type == self.type and c.data.get(LEMMA_STR) == self.data.get(LEMMA_STR)]
        return heads[0] if heads else None
    def get_args(self) -> List[tuple]:
        """ Returns the children attached to the tree and the rules they were attached by
        for nodes of the same type with the same lemma beneath this tree
        """
        node = self
        arglist = []
        while node:
            next = node.get_head_child()
            others = [c for c in node.children if c != next]
            arglist += [(child, node.rule) for child in others]
            node = next
        return arglist
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
    def from_data_list(data_list : List[NodeData]):
        return ParseSquare([Tree(data) for data in data_list])

class Parser:
    def __init__(self, grammar : Grammar):
        self.grammar = grammar
        self.table = list()
    def parse(self, input : List[ParseSquare], prune_similar = True):
        N = len(input)
        self.generate_table(N)
        for sq in input: # verify input -- no cell empty
            if not sq: raise Exception('Empty input cell')
        self.table[0] = [sq for sq in input] # initialize bottom row
        for row_index in range(0, len(self.table)):
            for col_index in range(0, len(self.table[row_index])):
                square = self.table[row_index][col_index]
                self.do_doubleton_rules(row_index, col_index, prune_similar)
                self.do_singleton_rules(square, prune_similar)
                square.sort(key=lambda t: -t.score)
        return self.table
    def generate_table(self, N : int):
        self.table = list() # array that holds the rows        
        for row_index in range(0, N): # create row
            row = [ParseSquare() for col in range(row_index, N)]
            self.table.append(row)
    def do_singleton_rules(self, square : ParseSquare, prune_similar : bool):
        i = 0 # index of node in square
        while(i < len(square)):
            node = square[i]
            for rule in self.grammar.singletons:
                result = rule.apply([node.data])
                if not result: continue
                (data, annotations) = result
                new_node = Tree(data, rule, [node], annotations)
                similar = [t for t in square if new_node.is_similar(t)]
                if not prune_similar or (prune_similar and not similar):
                    square.append(new_node)
            i += 1
    @staticmethod
    def generate_child_squares(row_index : int, col_index : int) -> List[tuple]:
        return [((s, col_index),(row_index-s-1, col_index+s+1)) for s in range(0, row_index)]
    def do_doubleton_rules(self, row_index : int, col_index : int, prune_similar : bool):
        square = self.table[row_index][col_index]
        for ((r1, c1), (r2, c2)) in Parser.generate_child_squares(row_index, col_index):
            child_sq1 = self.table[r1][c1]
            child_sq2 = self.table[r2][c2]
            for node1, node2 in [(n1, n2) for n1 in child_sq1 for n2 in child_sq2]: 
                for rule in self.grammar.doubletons:
                    result = rule.apply([node1.data, node2.data])
                    if not result: continue # rule could not be applied
                    (data, annotations) = result
                    new_node = Tree(data, rule, [node1, node2], annotations)
                    similar = [t for t in square if new_node.is_similar(t)] # list of trees similar to new_node
                    if not prune_similar or (prune_similar and not similar): # to ommit if similar
                        square.append(new_node)        

    def get_parses(self, position : tuple = None) -> List[List[Tree]]:
        (row, col) = position if position else (len(self.table)-1, 0)
        if self.table[row][col]: return [self.table[row][col]]
        # try children positions
        combos = []
        for possible_children in Parser.generate_child_squares(row, col):
            (childpos1, childpos2) = possible_children
            parses1 = self.get_parses(childpos1)
            parses2 = self.get_parses(childpos2)
            combos += [l1 + l2 for l1 in parses1 for l2 in parses2] # concatenate combinations
        return combos
    def to_jsonable(self):
        tree_list = []
        N = len(self.table)
        table = list()  # array that holds the rows        
        for row_index in range(0, N):  # create row
            row = [list() for col in range(row_index, len(self.table))]
            table.append(row)
            for col_index in range(0, len(row)):
                for tree in self.table[row_index][col_index]:
                    table[row_index][col_index].append(len(tree_list)) #this will be the tree ID
                    tree_list.append(tree)  # tree ID is index of tree in list
        tree_json_list = []
        for i in range(0, len(tree_list)):
            tree_json = tree_list[i].to_jsonable()
            tree_json['id'] = i
            tree_json['children'] = [tree_list.index(child) for child in tree_list[i].children]
            tree_json_list.append(tree_json)
        return {'nodes':tree_json_list, 'table':table}
            
