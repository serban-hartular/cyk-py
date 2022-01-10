from typing import List

import pyconll

from cyk.grammar import Grammar
import cyk.grammar_loader
from cyk.piecewise_parser import PiecewiseParser
from cyk.parser import Tree as CYK_Tree, ParseSquare

from pyconll.tree.tree import Tree as ConlluTree
from pyconll.unit.token import Token
from pyconll.unit.sentence import Sentence

from dictionary import word_2_parse_square
from ud_train.convert_to_ud import UD_Node, to_ud
from ud_train.process_conllu import elim_upos_from_conllu


def match_cyk_conllu(conllu : ConlluTree, parser : PiecewiseParser, sentence : Sentence) -> list:
    id = int(conllu.data.id)-1
    projection = [id]
    # figure out projection
    for child in conllu:
        child_proj = match_cyk_conllu(child, parser, sentence)
        if not child_proj:
            return []
        projection += child_proj
    projection.sort()
    # check consecutive
    for i in range(1, len(projection)):
        if projection[i] - projection[i-1] != 1:
            print('Projection not continuous: ' + str(projection))
            return []
    # try parse of span
    span = range(projection[0], projection[-1]+1)
    #make a copy
    ud_tokens = [Token(t.conll()) for t in sentence[span.start:span.stop]]
    #make root token head 0
    for tok in ud_tokens:
        if tok.id == conllu.data.id:
            tok.head = '0'
    # start trying out parses
    matching_trees = []
    while True:
        nodes_added = parser.parse_span(span)
        # print(nodes_added)
        if nodes_added == 0:
            if len(projection) == 1:
                return projection
            else:
                print('No more parses for span [%d...%d)' % (span.start, span.stop))
                return []
        if len(projection) == 1:
            continue
        (row, col) = parser.latest_nodes[-1]
        root = parser.table[row][col]
        for tree in root:
            node_list = UD_Node.token_list(to_ud(tree)[0])
            if not UD_Node.differences(node_list, ud_tokens):
                matching_trees.append(tree)
        if matching_trees:
            break
    # done looking for trees
    # check for matching tree
    if not matching_trees:
        print('No matching parse found for span [%d...%d)' % (span.start, span.stop))
        return []
    # eliminate all but matching tree
    for (row, col) in parser.latest_nodes:
        parser.table[row][col].clear()
    (row, col) = parser.latest_nodes[-1]
    parser.table[row][col].extend(matching_trees)
    # return projection
    return projection



filename = '../corpus_ud/ro_rrt-ud-dev.conllu'
sentences = [s for s in pyconll.iter_from_file(filename)]
sentences.sort(key=lambda s : len(s))

grammar_lines = []
with open('../ro_locut.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
with open('../rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
grammar = Grammar(cyk.grammar_loader.load_rules(grammar_lines))
parser = PiecewiseParser(grammar)

not_continuous = [
    'dev-312', # bad annot
    'dev-92', #  Comitetul O.N.U. împotriva torturii cere explicații SUA și Marii Britanii în legătură cu tratamentele inumane aplicate deținuților irakieni.
    'dev-450', 'dev-443', 'dev-444', 'dev-445',  # putea 
    'dev-180', 'dev-516', # trebui
    'dev-630',   # urma
]

problem = ['dev-18',  # secundele treceau una dupa alta -- predsup?
         'dev-78', # este un om instarit -- xcomp in annot
         'dev-340', # Singură specia umană (Adj nearticulat inainte de NP)
         'dev-361', # uneia sau mai multor enzime (NP?)
         'dev-39',  # se aplecara sa-l ia de brate -- cauzativ?
         'dev-408', # Sarcina Spuneti imediat...
         'dev-484', # problema
]

npe = [ 'dev-452', 'dev-509', 'dev-510']

vmod = [
    'dev-352', # putea
    'dev-600', 'dev-366', 'dev-511'# trebui
]

ellipsis = ['dev-307', 'dev-339']

no_do = not_continuous + problem + npe + vmod + ellipsis

for sentence in sentences:
    if sentence.id in no_do:
        continue
    has_shit = False
    for i, token in enumerate(sentence):
        if token.upos in ['SYM', 'INTJ'] or (token.upos in ['PUNCT'] and i != len(sentence) - 1):
            has_shit = True
            break
    if has_shit:
        continue
    # eliminate last punctuation
    if sentence[-1].upos in ['PUNCT']:
        conll = sentence.conll()
        lines = conll.split('\n')
        lines = lines[:-1] # skip last
        conll = '\n'.join(lines)
        sentence = Sentence(conll)
    print(sentence.id, sentence.text)
    ud_tokens = elim_upos_from_conllu(sentence, ['PUNCT', 'INTJ'])
    # feed tokens to dictionary for sq_list
    sq_list = [word_2_parse_square(token.form, str(i + 1)) for i, token in enumerate(ud_tokens)]
    # print(sq_list)
    parser.input(sq_list)
    proj = match_cyk_conllu(sentence.to_tree(), parser, sentence)
    if not proj:
        print('No parse found ' + sentence.id)
