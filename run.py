from dictionary import text_2_square_list
from cyk_parser import Parser, Grammar
from cyk_grammar_loader import load_grammar

import rom_cfg_nom
import rom_cfg_verb

grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
# """
# %%alias Case,Gender,Number CGN 
# %%alias lemma L
# %%alias HasDet,HasQuant DQ
# NP[CGN=@] ::= NOUN[CGN=@]
# NP[CGN=@ DQ=T] ::= DET[CGN=@] NP[CGN=@ DQ=F] 
# """

def parse(text : str, parser : Parser) -> bool:
    try:
        sq_list = text_2_square_list(text)
    except Exception as e:
        print(e)
        return False
    parser.parse(sq_list)
    return True

if __name__ == "__main__":
    grammar = load_grammar(grammar_rules)
    parser = Parser(grammar)
    if parse('Tu mergi la gară', parser):
        p = parser.get_parses()
        p.sort(key=lambda n: len(n))
        p = parser.get_parses()[0]
        print(p[0].detail2())
