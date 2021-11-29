from dictionary import text_2_square_list, word_2_parse_square
from cyk_parser import Parser, Grammar
from cyk_grammar_loader import load_grammar

import rom_cfg_nom
import rom_cfg_verb

# """
# %%alias Case,Gender,Number CGN 
# %%alias lemma L
# %%alias HasDet,HasQuant DQ
# NP[CGN=@] ::= NOUN[CGN=@]
# NP[CGN=@ DQ=T] ::= DET[CGN=@] NP[CGN=@ DQ=F] 
# """

grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
# grammar_rules = """
# VP ::= h:VERB
# VP ::= NP[Case=Nom Person=@ Number=@] VP[Person=@ Number=@]
# NP[Person=3] ::= h:NOUN
# NP ::= h:PRON
# """

from prob_parser import ProbabilisticParser

with open('rom_cfg_0.1.cfg', 'r', encoding='utf8') as fptr:
    grammar = load_grammar(fptr)
parser_old = Parser(grammar)
parser = ProbabilisticParser(grammar)
def parse(text : str, _parser : ProbabilisticParser = parser):
    sq_list, unknown = text_2_square_list(text)
    if unknown:
        print('Unkown: ' + ', '.join(unknown))
    _parser.input(sq_list)
    return _parser.next_parse()

from guess_tree import guess_tree
from cyk_parser import *

from ud_train.convert_to_ud import *
from ud_train.process_conllu import *
import pyconll

# if __name__ == '__main__':
#     filename = './corpus_ud/ro_rrt-ud-dev.conllu'
# 
#     conll = pyconll.load_from_file(filename)
#     # sort by shortest
#     sentence_list = [s for s in conll]
#     sentence_list.sort(key=lambda s: len(s))
#     for sentence in sentence_list:
#         # get a parsed sentence
#         ud_tokens = elim_upos_from_conllu(sentence, ['PUNCT', 'INTJ'])
#         # feed tokens to dictionary for sq_list
#         sq_list = [word_2_parse_square(token.form, str(i+1)) for i, token in enumerate(ud_tokens)]
#         parser.input(sq_list)
#         # look for parse that matches
#         matching_parse = None
#         while parser.next_parse() > 0:
#             tree = parser.root()[-1]
#             node_list = UD_Node.token_list(to_ud(tree)[0])
#             if not UD_Node.differences(node_list, ud_tokens):
#                 matching_parse = tree
#                 break
#         if matching_parse is None: # didn't find parse
#             print("Couldn't find parse for " + sentence.text)
#             break
#  