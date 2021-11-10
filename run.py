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

# grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
grammar_rules = """
%%alias VerbForm,Mood,Tense,Person,Number,lemma VMTPNL
%%alias Mood,Tense,Person,Number,lemma MTPNL

V0[VerbForm=Gaa Person=@] ::= h:VERB[VerbForm=Fin,Ger] PRON[Person=@]
"""

grammar = load_grammar(grammar_rules)
parser = Parser(grammar)

def parse(text : str, _parser : Parser = parser):
    try:
        sq_list = text_2_square_list(text)
    except Exception as e:
        print(e)
        return False
    _parser.parse(sq_list)
    return _parser.get_parses()[0]

