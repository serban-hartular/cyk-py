
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
        text = '"' + self.form + '"'
        text += self.data[TYPE_STR].get() if TYPE_STR in self.data.keys() else ''
        other_keys = [k for k in self.data.keys() if k not in [FORM_STR, TYPE_STR]]
        if other_keys:
            text += '['
            text += ' '.join([k + '=' + ','.join(self.data[k]) for k in other_keys])
            text += ']'
        text += ' -- %s' % str(self.rule) if self.rule else ''
        return text
    def __repr__(self):
        return str(self)

class ParseSquare(List[Tree]):
    def __init__(self, tree_list : List[Tree] = list()):
        super().__init__(tree_list)
    def from_data_list(data_list : List[NodeData]):
        return ParseSquare([Tree(data) for data in data_list])

class Parser:
    def __init__(self, grammar : Grammar):
        self.grammar = grammar
    def parse(self, input : List[ParseSquare], prune_similar = True):
        N = len(input)
        table = self.generate_table(N)
        table[0] = [sq for sq in input] # initialize bottom row
        for row_index in range(0, len(table)):
            for col_index in range(0, len(table[row_index])):
                # print('%d, %d' % (row_index, col_index))
                square = table[row_index][col_index]
                self.do_doubleton_rules(table, row_index, col_index, prune_similar)
                self.do_singleton_rules(square, prune_similar)
        return table
    def generate_table(self, N : int):
        table = list() # array that holds the rows        
        for row_index in range(0, N): # create row
            row = [ParseSquare() for col in range(row_index, N)]
            table.append(row)
        return table
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
    
    def do_doubleton_rules(self, table, row_index : int, col_index : int, prune_similar : bool):
        square = table[row_index][col_index]
        # for span in range(0, row_index):
        #     child_sq1 = table[span][col_index] #this guy's length is span+1
        #     child_sq2 = table[row_index-span-1][col_index+span+1] # this guy's is row_index - span - 1
        for ((r1, c1), (r2, c2)) in Parser.generate_child_squares(row_index, col_index):
            child_sq1 = table[r1][c1]
            child_sq2 = table[r2][c2]
            # print('%d, %d  <- %d, %d; %d, %d' % (row_index, col_index, span, col_index, row_index-span-1, col_index+span+1))
            for node1, node2 in [(n1, n2) for n1 in child_sq1 for n2 in child_sq2]: #zip(child_sq1, child_sq2):
                # if (row_index, col_index) == (2, 0):
                #     print(node1.data, node2.data)
                for rule in self.grammar.doubletons:
                    result = rule.apply([node1.data, node2.data])
                    if not result: continue
                    new_node = Tree(result, rule, [node1, node2])
                    similar = [t for t in square if new_node.is_similar(t)]
                    if not prune_similar or (prune_similar and not similar):
                        square.append(new_node)

    
    # NP ::= AdjP
if __name__ == '__main__':    
    from values import Values
    from rule_io import rule_list_from_string

    grammar_rules = """
    NP[caz=@ gen=@] ::= N[caz=@ gen=@]
    AdjP ::= Adj
    NP[caz=@ gen=@] ::= NP[caz=@ gen=@] AdjP
    NP[caz=@ gen=@] ::= DetP NP[caz=@ gen=@]
    DetP ::= Det
    """

    grammar = Grammar(rule_list_from_string(grammar_rules))
    
    parser = Parser(grammar)
    input = [
        NodeData({'form':Values(['un']),     'type':Values(['Det'])}),
        NodeData({'form':Values(['baiat']), 'type':Values(['N']), 'gen':['masc', 'fem']}),
        NodeData({'form':['frumos'], 'type':['Adj']}),
    ]    
    input_squares = [ParseSquare.from_data_list([d]) for d in input]
    table = parser.parse(input_squares)
    
    
