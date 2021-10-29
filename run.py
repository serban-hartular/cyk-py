from dictionary import text_2_square_list
from cyk_parser import Parser, Grammar
from cyk_grammar_loader import load_grammar

grammar_rules = """
%%alias Case,Gender,Number CGN 
%%alias lemma L
NP[CGN=@] ::= NOUN[CGN=@ L=omi]
NP[CGN=@ HasDet=T] ::= DET[CGN=@] NP[CGN=@ HasDet=F] 
"""

def parse(text : str, parser : Parser):
    try:
        sq_list = text_2_square_list(text)
    except Exception as e:
        print(e)
        return 
    parser.parse(sq_list)

grammar = load_grammar(grammar_rules)
parser = Parser(grammar)
parse('un om', parser)
p = parser.get_parses()[0][0]



