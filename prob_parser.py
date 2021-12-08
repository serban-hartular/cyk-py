from cyk_parser import *

class ProbabilisticParser(Parser):
    def __init__(self, grammar : Grammar):
        super().__init__(grammar)
        self.input_row = list()
        self.N = 0
        self.exclude_similar = True
    def input(self, input : List[ParseSquare], exclude_similar = True):
        self.N = len(input)
        self.exclude_similar = exclude_similar
        self.generate_table(self.N)
        self.table[0] = [sq for sq in input]  # initialize bottom row
    # def _max_score(self, row, col):
    #     if not self.table[row][col]:
    #         return -9999999
    #     return max([t.nscore for t in self.table[row][col]])
    def next_parse(self) -> int:
        nodes_added = 0
        for row in range(0, self.N):
            for col in range(0, len(self.table[row])):
                # first do _doubletons
                possible_trees = ParseSquare([])
                for ((r1, c1), (r2, c2)) in Parser.generate_child_squares(row, col):
                    child_sq1 = self.table[r1][c1]
                    child_sq2 = self.table[r2][c2]
                    for node1, node2 in [(n1, n2) for n1 in child_sq1 for n2 in child_sq2]:
                        for rule in self.grammar.get_rules((None, str(node1.data[TYPE_STR]), str(node2.data[TYPE_STR]))): #self.grammar._doubletons:
                            (data, annotations) = rule.apply([node1.data, node2.data])
                            if not data: continue  # rule could not be applied
                            new_node = Tree(data, rule, [node1, node2], annotations)
                            # similar = [t for t in self.table[row][col] if new_node.is_similar(t)]  # list of trees similar to new_node
                            # if not self.exclude_similar or (self.exclude_similar and not similar):  # to ommit if similar
                            #     possible_trees.append(new_node) 
                            if not self.table[row][col].contains_similar(new_node):
                                possible_trees.append(new_node)
                if possible_trees:
                    possible_trees.sort(key=lambda t : t.nscore)
                    self.table[row][col].append(possible_trees[-1])
                    nodes_added += 1
                # do _singletons
                i = 0
                while i < len(self.table[row][col]):
                    node = self.table[row][col][i]
                    for rule in self.grammar.get_rules((None, str(node.data[TYPE_STR]))):#self.grammar._singletons:
                        (data, annotations) = rule.apply([node.data])
                        if not data: continue
                        new_node = Tree(data, rule, [node], annotations)
                        similar = [t for t in self.table[row][col] if new_node.is_similar(t)]
                        if not self.exclude_similar or (self.exclude_similar and not similar):
                            self.table[row][col].append(new_node)
                            nodes_added += 1
                        # nodes_added += self.table[row][col].add(new_node, self.exclude_similar)
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
