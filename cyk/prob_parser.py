from collections import Set
from typing import Iterable

from cyk.parser import *

class ProbParseSquare(ParseSquare):
    def __init__(self, tree_list : List[Tree] = list()):
        super().__init__(tree_list)
        self.rules_tried = set() # to keep track of what rules have been tried
    @staticmethod
    def to_rule_tried(tree : Tree) -> tuple:
        return (tree.rule,) + tuple(tree.children)
    def append(self, tree: Tree) -> None:
        super().append(tree)
        if tree.rule:
            self.rules_tried.add(ProbParseSquare.to_rule_tried(tree))
    def extend(self, trees: Iterable[Tree]) -> None:
        super().extend(trees)
        self.rules_tried = self.rules_tried.union(
            [ProbParseSquare.to_rule_tried(tree) for tree in trees if tree.rule])
    def remove(self, tree : Tree) -> None:
        super().remove(tree)
        if tree.rule:
            self.rules_tried.remove(ProbParseSquare.to_rule_tried(tree))
    def clear(self) -> None:
        super().clear()
        self.rules_tried.clear()
    @staticmethod
    def new(tree_list : List[Tree] = list()):
        return ProbParseSquare(tree_list)
        
class ProbabilisticParser(Parser):
    def __init__(self, grammar : Grammar):
        super().__init__(grammar)
        self.input_row = list()
        self.N = 0
        self.exclude_similar = True
    def input(self, input : List[ParseSquare], exclude_similar = True):
        self.N = len(input)
        self.exclude_similar = exclude_similar
        self.generate_table(self.N, ProbParseSquare.new)
        self.table[0] = [ProbParseSquare.new(sq) for sq in input]  # initialize bottom row
    # def _max_score(self, row, col):
    #     if not self.table[row][col]:
    #         return -9999999
    #     return max([t.nscore for t in self.table[row][col]])
    @staticmethod
    def regular_order(N : int) -> tuple:
        for row in range(0, N):
            for col in range(0, N-row):
                yield (row, col)
    @staticmethod
    def word_order(N : int) -> tuple:
        for diagonal in range(0, N):
            for back in range(0, diagonal+1):
                yield (back, diagonal-back)
    def next_parse(self, coord_generator = None) -> int:
        nodes_added = 0
        if coord_generator is None:
            coord_generator = ProbabilisticParser.word_order    #ProbabilisticParser.regular_order
        # for row in range(0, self.N):
        #     for col in range(0, len(self.table[row])):
        for (row, col) in coord_generator(self.N):
            nodes_added += self.do_square(row, col)
        return nodes_added
    
    def do_square(self, row: int, col: int) -> int:
        nodes_added = 0
        square : ProbParseSquare = self.table[row][col]
        # first do _doubletons
        possible_trees = ParseSquare([])
        for ((r1, c1), (r2, c2)) in Parser.generate_child_squares(row, col):
            child_sq1 = self.table[r1][c1]
            child_sq2 = self.table[r2][c2]
            for node1, node2 in [(n1, n2) for n1 in child_sq1 for n2 in child_sq2]:
                for rule in self.grammar.get_rules((None, str(node1.data[TYPE_STR]), str(node2.data[TYPE_STR]))): #self.grammar._doubletons:
                    if (rule, node1, node2) in square.rules_tried:
                        continue
                    (data, annotations) = rule.apply([node1.data, node2.data])
                    if not data: continue  # rule could not be applied
                    new_node = Tree(data, rule, [node1, node2], annotations)
                    # if not self.exclude_similar or \
                    #     not square.contains_similar(new_node):
                    #     possible_trees.append(new_node)
                    if square.contains_similar(new_node) and self.exclude_similar:
                        square.rules_tried.add((rule, node1, node2))    
                    else:
                        possible_trees.append(new_node)
        if possible_trees:
            possible_trees.sort(key=lambda t : t.nscore)
            square.append(possible_trees[-1])
            nodes_added += 1
        # do _singletons
        i = 0
        while i < len(square):
            node = square[i]
            for rule in self.grammar.get_rules((None, str(node.data[TYPE_STR]))):#self.grammar._singletons:
                if (rule, node) in square.rules_tried:
                    continue
                (data, annotations) = rule.apply([node.data])
                if not data: continue
                new_node = Tree(data, rule, [node], annotations)
                similar = [t for t in square if new_node.is_similar(t)]
                # if not self.exclude_similar or (self.exclude_similar and not similar):
                #     square.append(new_node)
                #     nodes_added += 1
                if similar and self.exclude_similar:
                    square.rules_tried.add((rule, node))
                else:
                    square.append(new_node)
                    nodes_added += 1
            i += 1
        return nodes_added
    def table_copy(self) -> 'ProbabilisticParser':
        """Creates its own table and copies trees from original to its own table.
        Does not create deep copies of the trees. """
        cp = ProbabilisticParser(self.grammar)
        cp.N = self.N
        cp.exclude_similar = self.exclude_similar
        cp.generate_table(self.N)
        for row in range(0, self.N):
            for col in range(0, len(self.table[row])):
                cp.table[row][col] = ParseSquare(self.table[row][col])
        return cp
