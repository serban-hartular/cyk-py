from dictionary import text_2_square_list
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

if __name__ == '__main__':
    # from rule import *
    # from guess_tree import *
    print(parse('Ion are *** fete'))
    guesser = parser.table_copy()
    guess_tree(guesser, NodeData({'type':'VP'}), add_guesses=True)
    guesser.to_jsonable()
