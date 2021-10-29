
from rule import Rule, NodeData
from rule_io import TYPE_STR, FORM_STR
from typing import List

# FORM_STR = rule.FORM_STR

class Grammar:
    def __init__(self, rules : List[Rule]):
        self.rules = rules
        self.singletons = [r for r in rules if len(r.children) == 1]
        self.doubletons = [r for r in rules if len(r.children) == 2]
        others = [r for r in rules if len(r.children) != 1 and len(r.children) != 2]
        if others:
            raise Exception("Rules can only have 1 or 2 children: '%s'" % others[0].to_text())

class Tree:
    def __init__(self, data : NodeData, rule : Rule = None, children : List['Tree'] = []):
        self.data = data
        self.children = children
        self.rule = rule
        self.score = 1
        if not children:
            self.form = ' '.join([s for s in data[FORM_STR]]) if FORM_STR in data else ''
        else:
            self.form = ' '.join([c.form for c in self.children])
    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()
    def is_similar(self, other : 'Tree') -> bool:
        # consider them similar if they have the same leaves and were obtained following the same rules
        leaves1 = [l for l in self.traverse() if not l.children]
        leaves2 = [l for l in other.traverse() if not l.children]
        rules1 = [n.rule for n in self.traverse() if n]
        rules2 = [n.rule for n in other.traverse() if n]
        return set(leaves1) == set(leaves2) and set(rules1) == set(rules2)
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
                new_node = Tree(result, rule, [node])
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
                    new_node = Tree(result, rule, [node1, node2])
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
        
    # NP ::= AdjP
if __name__ == '__main__':    
    from values import Values
    from rule_io import rule_list_from_string
    from cyk_grammar_loader import load_grammar

    grammar_rules = """
    %%group gen,nr,caz GNC
    NP[GNC=@] ::= N[GNC=@]
    AdjP[GNC=@] ::= Adj[GNC=@]
    NP[GNC=@] ::= NP[GNC=@] AdjP[GNC=@]
    NP[GNC=@] ::= DetP[GNC=@] NP[GNC=@]
    DetP[GNC=@] ::= Det[GNC=@]
    PP ::= ADP[caz=@] NP[caz=@]
    VP ::= NP[caz!=Dat] VERB
    VP ::= VP PP
    NP[GNC=@] ::= NP[GNC=@] PP
    """

    grammar = load_grammar(grammar_rules)
    
    parser = Parser(grammar)
    input = [
        NodeData({'form': 'Ion', 'type': 'N'}),
        NodeData({'form':'merge', 'type':'VERB'}),
        NodeData({'form': 'cu', 'type': 'ADP'}),
        NodeData({'form': 'spada', 'type': 'N'}),
        NodeData({'form': 'in', 'type': 'ADP'}),
        NodeData({'form': 'lume', 'type': 'N'}),

        # NodeData({'form':'o', 'type':'Det', 'nr':'sg', 'gen':'fem'}),
        # NodeData({'form':'dansatoare', 'type':'N', 'gen':'fem'}),
        # NodeData({'form':'frumoase', 'type':'Adj', 'nr':'pl', 'gen':'fem'}),
    ]    
    input_squares = [ParseSquare.from_data_list([d]) for d in input]
    table = parser.parse(input_squares)
    
    
