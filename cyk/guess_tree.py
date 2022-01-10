from cyk.parser import *
from cyk.prob_parser import *

def _empty(parser : Parser, pos : tuple) -> bool:
    return not bool([t for t in parser.cell(pos) if not t.guess and parser.grammar.is_known(t.type)])
    
def greedy_guess_tree(parser : Parser, guess_root : NodeData, pos : tuple = None, **kwargs) -> List[Tree]:
    add_guesses = kwargs.get('add_guesses') is True
    exclude_similar = False if kwargs.get('exclude_similar') == False else True
    if pos is None:
        pos = (len(parser.table)-1, 0)  # top cell

    # do bottom row if there, and return
    if guess_root[TYPE_STR].get() in parser.grammar.terminals and pos[0] == 0: # bottom row
        unknowns = [t for t in parser.cell(pos) if not parser.grammar.is_known(t.type)]
        form = unknowns[0].form if unknowns else ''
        guess_root = NodeData(guess_root)
        guess_root[FORM_STR] = form
        # print('returning terminal ' + str(guess_root))
        t = Tree(guess_root, None, None, None, True)
        if add_guesses:
            if parser.table[pos[0]][pos[1]].contains_similar(t):
                return []
            parser.table[pos[0]][pos[1]].add(t, exclude_similar)
        return [t]

    # next do doubletones
    guess_list = []
    for childpos1, childpos2 in parser.generate_child_squares(pos[0], pos[1]):
        # print(guess_root, childpos1, childpos2)
        if not _empty(parser, childpos1) and not _empty(parser, childpos2):
            # raise Exception('Parses present in children {}, {} of {}'.format(str(pos), str(childpos1), str(childpos2)))
            continue #return None
        if _empty(parser, childpos1) and _empty(parser, childpos2):
            # raise Exception(
            #     'Parses absent in children both {}, {} of {}'.format(str(pos), str(childpos1), str(childpos2)))
            continue 
            # return None
        if _empty(parser, childpos1):
            missing_index = 1
            guess_pos, existing_pos = (childpos1, childpos2)
        else:
            missing_index = 2
            guess_pos, existing_pos = (childpos2, childpos1)
        for existing in parser.cell(existing_pos):
            candidate_kids = [None, existing.data] if missing_index == 1 else [existing.data, None]
            # print(candidate_kids)
            for rule in parser.grammar._doubletons:
                nodes, annot = rule.solve_for_child([guess_root] + candidate_kids)
                if not nodes: continue # could not apply rule
                # print(rule, nodes)
                solved = nodes[missing_index]
                kids_guesses = greedy_guess_tree(parser, solved, guess_pos, **kwargs) # list of possible guesses based on solved
                if kids_guesses is None: return None
                new_parents = []
                # for kid in kids_guesses:
                #     child_list = [kid, existing] if missing_index == 1 else [existing, kid]
                #     parent_data = rule.apply([t.data for t in child_list])
                #     new_parents.append(Tree(parent_data, rule, child_list, 
                #                     annot, True))
                new_parents = [Tree(nodes[0], rule, [kid, existing] if missing_index == 1 else [existing, kid], 
                                    annot, True) for kid in kids_guesses]
                guess_list += new_parents
    # try _singletons
    # print('Singleton: ', guess_root, pos)
    for rule in parser.grammar._singletons:
        nodes, annot = rule.solve_for_child([guess_root, None])
        if not nodes: continue
        (root, child_data) = nodes
        child_guesses = greedy_guess_tree(parser, child_data, pos, **kwargs) # these are trees
        if child_guesses is None: return None
        if not child_guesses: continue # no guess found
        guess_list += [Tree(root, rule, [child], annot, True) for child in child_guesses]
    
    if exclude_similar:
        guess_list = [t for t in guess_list if not parser.table[pos[0]][pos[1]].contains_similar(t)]
    if add_guesses:
        parser.table[pos[0]][pos[1]] += guess_list
        # parser.table[pos[0]][pos[1]].add(guess_list, exclude_similar)

    return guess_list

class GuessTree(Tree):
    def __init__(self, pos : tuple, data : NodeData, rule : Rule = None, children : List['Tree'] = None, children_annot : List[Dict] = None, parent : 'GuessTree' = None):
        self.data = data
        self.pos = pos
        self.parent = parent
        self.children = children if children else list()
        self.children_annot = children_annot
        self.rule = rule
        self.score = 1
        self.num_nodes = 1 + sum([child.num_nodes for child in self.children if child])
        self.nscore = 0
        if not children:
            self.form = ' '.join([s for s in data[FORM_STR]]) if FORM_STR in data else ''
        else:
            self.form = ' '.join([c.form for c in self.children if c])
        self.type = self.data[TYPE_STR].get() if TYPE_STR in self.data.keys() else '?'
        self.assign_score()
        self.guess = True
        self.unknown_child_pos = None
        self.unknown_child_data = None
    def assign_score(self):
        self.num_nodes = 1 + sum(child.num_nodes for child in self.children if child)
        self.score = self.rule.score if self.rule else 1
        for child in self.children:
            if child:
                self.score *= child.score
        self.nscore = math.log10(self.score) / self.num_nodes
    def __str__(self):
        if len(self.children) < 2:
            text = '"' + self.form + '"'
        else:
            (form0, form1) = tuple([child.form if child else 'None' for child in self.children])
            text = '"' + form0 + '|' + form1 + '"'
        text += self.data[TYPE_STR].get() if TYPE_STR in self.data.keys() else ''
        other_keys = [k for k in self.data.keys() if k not in [FORM_STR, TYPE_STR]]
        if other_keys:
            text += '('
            text += ' '.join([k + '=' + ','.join(self.data[k]) for k in other_keys])
            text += ')'
        return text


class GuessTable(ProbabilisticParser):
    def __init__(self, parser : ProbabilisticParser, root_data : NodeData):
        """
        Copies the contents of the parser's table
        """
        super().__init__(parser.grammar)
        self.N = parser.N
        self.exclude_similar = parser.exclude_similar
        self.generate_table(parser.N)
        for row in range(0, self.N):
            for col in range(0, len(self.table[row])):
                self.table[row][col] = ParseSquare(parser.table[row][col])
        self.open_nodes : List[GuessTree] = []
        self.root_data = root_data
        # seed first guesses
        self.open_nodes = self.complete_head(root_data)
        self.solution_nodes : List[GuessTree] = []
    def has_next_guess(self) -> bool:
        return bool(self.open_nodes)
    def expand_open_node(self):
        if not self.open_nodes:
            return
        # sort queue, best is last
        self.open_nodes.sort(key=GuessTable.node_rank)
        candidate = self.open_nodes.pop()
        guesses = self.complete_head(candidate.unknown_child_data, candidate.unknown_child_pos)
        for guess in guesses:
            guess.parent = candidate
            if guess not in self.solution_nodes:
                self.open_nodes.append(guess)
    @staticmethod    
    def node_rank(node : GuessTree):
        # best node last: closest to bottom row and best normalized score
        return -node.pos[0] + node.nscore
    def complete_head(self, guess_data : NodeData, pos : tuple = None) -> List[GuessTree]:
        if pos is None: pos = (self.N - 1, 0)
        generated_nodes = []
        # check if it's a terminal node
        if guess_data[TYPE_STR].get() in self.grammar.terminals:
            # if we're on the bottom row, yay! else, no joy
            if pos[0] == 0:
                data = NodeData(guess_data) # make a copy, we'll add the form
                data[FORM_STR] = self.table[pos[0]][pos[1]][0].form \
                    if self.table[pos[0]][pos[1]][0] else '?'
                node = GuessTree(pos, data)
                self.solution_nodes.append(node)
                return [node]
            return []

        for((r1, c1), (r2, c2)) in self.generate_child_squares(pos[0], pos[1]):
            child_sq1 = self.table[r1][c1]
            for existing in [t for t in child_sq1 if not t.guess]:
                for rule in self.grammar.get_rules(
                        [str(guess_data[TYPE_STR]),str(existing.data[TYPE_STR]), None]):#self.grammar._doubletons:
                    if rule in [t.rule for t in self.table[pos[0]][pos[1]]]:
                        continue  # we already have a node that applied this rule
                    nodes, annot = rule.solve_for_child([guess_data, existing.data, None])
                    if nodes:
                        new_parent = GuessTree(pos, nodes[0], rule, [existing, None], annot)
                        new_parent.unknown_child_pos = (r2, c2)
                        new_parent.unknown_child_data = nodes[2]
                        generated_nodes.append(new_parent)
            child_sq2 = self.table[r2][c2]
            for existing in [t for t in child_sq2 if not t.guess]:
                for rule in self.grammar.get_rules(
                        [str(guess_data[TYPE_STR]), None, str(existing.data[TYPE_STR])]): #self.grammar._doubletons:
                    if rule in [t.rule for t in self.table[pos[0]][pos[1]]]:
                        continue  # we already have a node that applied this rule
                    nodes, annot = rule.solve_for_child([guess_data, None, existing.data])
                    if nodes:
                        new_parent = GuessTree(pos, nodes[0], rule, [None, existing], annot)
                        new_parent.unknown_child_pos = (r1, c1)
                        new_parent.unknown_child_data = nodes[1]
                        generated_nodes.append(new_parent)
        # # now do singleton _rules
        for rule in self.grammar._singletons:
            nodes, annot = rule.solve_for_child([guess_data, None])
            if not nodes: continue
            new_parent = GuessTree(pos, nodes[0], rule, [None], annot)
            new_parent.unknown_child_pos = pos
            new_parent.unknown_child_data = nodes[1]
            generated_nodes.append(new_parent)
        # self.open_nodes += generated_nodes
        return generated_nodes
    def guess(self) -> bool:
        while self.has_next_guess() and not self.solution_nodes:
            self.expand_open_node()
        if not self.solution_nodes:
            return False
        node_stack : List[(Tree, tuple)] = []
        solution = self.solution_nodes.pop()
        node = Tree(solution.data, solution.rule, solution.children, solution.children_annot, True)
        # self.table[solution.pos[0]][solution.pos[1]].append(node)
        node_stack.append((node, solution.pos))
        parent = solution.parent
        while parent:
            # replace 'None' with the deduced chid node
            kids = [c if c is not None else node for c in parent.children]
            node = Tree(parent.data, parent.rule, kids, parent.children_annot, True)
            # self.table[parent.pos[0]][parent.pos[1]].append(node)
            node_stack.append((node, parent.pos))
            parent = parent.parent
        root = node
        # check if similar guess exists
        similar = [n for n in self.table[self.N-1][0] if n.guess and n.is_similar(root) and n is not root]
        if similar:
            # print('similar:\n%s\n%s' % (str(root), str(similar[0])))
            return True
        # add stack of nodes to table
        for (node, pos) in node_stack:
            self.table[pos[0]][pos[1]].append(node)
        return True
    