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


with open('rom_cfg_0.1.cfg', 'r', encoding='utf8') as fptr:
    grammar = load_grammar(fptr)
parser = Parser(grammar) #faster_parsers.PoolParser(grammar)

def parse(text : str, _parser : Parser = parser):
    sq_list, unknown = text_2_square_list(text)
    if unknown:
        print('Unkown: ' + ', '.join(unknown))
    _parser.parse(sq_list)
    return _parser.get_parses()

if __name__ == '__main__':
    from rule import *
    from guess_tree import *
    parse('un bou *** are fete')
    # parser.cell(0, 1).clear()
    vp = [r for r in grammar.doubletons if str(r).startswith('VP')]

    s = guess_tree(parser, NodeData({TYPE_STR:'VP'}), add_guesses=True)
    print(s)