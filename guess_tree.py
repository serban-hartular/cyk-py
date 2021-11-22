

from cyk_parser import *

def _empty(parser : Parser, pos : tuple) -> bool:
    return not bool([t for t in parser.cell(pos) if not t.guess and parser.grammar.is_known(t.type)])
    
def guess_tree(parser : Parser, guess_root : NodeData, pos : tuple = None, **kwargs) -> List[Tree]:
    add_guesses = kwargs.get('add_guesses') is True
    if pos is None:
        pos = (len(parser.table)-1, 0)  # top cell

    if guess_root[TYPE_STR].get() in parser.grammar.terminals and pos[0] == 0: # bottom row
        unknowns = [t for t in parser.cell(pos) if not parser.grammar.is_known(t.type)]
        form = unknowns[0].form if unknowns else ''
        guess_root = NodeData(guess_root)
        guess_root[FORM_STR] = form
        # print('returning terminal ' + str(guess_root))
        t = Tree(guess_root, None, None, None, True)
        if add_guesses: parser.table[pos[0]][pos[1]].append(t)
        return [t]

    # next do doubletones
    guess_list = []
    for childpos1, childpos2 in parser.generate_child_squares(pos[0], pos[1]):
        # print(guess_root, childpos1, childpos2)
        if not _empty(parser, childpos1) and not _empty(parser, childpos2):
            # raise Exception('Parses present in children {}, {} of {}'.format(str(pos), str(childpos1), str(childpos2)))
            return None
        if _empty(parser, childpos1) and _empty(parser, childpos2):
            # raise Exception(
            #     'Parses absent in children both {}, {} of {}'.format(str(pos), str(childpos1), str(childpos2)))
            return None
        if _empty(parser, childpos1):
            missing_index = 1
            guess_pos, existing_pos = (childpos1, childpos2)
        else:
            missing_index = 2
            guess_pos, existing_pos = (childpos2, childpos1)
        for existing in parser.cell(existing_pos):
            candidate_kids = [None, existing.data] if missing_index == 1 else [existing.data, None]
            # print(candidate_kids)
            for rule in parser.grammar.doubletons:
                nodes, annot = rule.solve_for_child([guess_root] + candidate_kids)
                if not nodes: continue # could not apply rule
                # print(rule, nodes)
                solved = nodes[missing_index]
                kids_guesses = guess_tree(parser, solved, guess_pos, **kwargs) # list of possible guesses based on solved
                if kids_guesses is None: return None
                # new_kids = [solved, existing] if missing_index == 1 else [existing, solved]
                new_parents = [Tree(nodes[0], rule, [kid, existing] if missing_index == 1 else [existing, kid], 
                                    annot, True) for kid in kids_guesses]
                guess_list += new_parents
    # try singletons
    # print('Singleton: ', guess_root, pos)
    for rule in parser.grammar.singletons:
        nodes, annot = rule.solve_for_child([guess_root, None])
        if not nodes: continue
        (root, child_data) = nodes
        child_guesses = guess_tree(parser, child_data, pos, **kwargs) # these are trees
        if child_guesses is None: return None
        if not child_guesses: continue # no guess found
        guess_list += [Tree(root, rule, [child], annot, True) for child in child_guesses]
    
    if add_guesses: parser.table[pos[0]][pos[1]] += guess_list
    return guess_list
    