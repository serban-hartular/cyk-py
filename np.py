from dictionary import text_2_square_list
from cyk_parser import Parser
from cyk_grammar import Grammar
from cyk_grammar_loader import load_grammar

grammar_rules = """
%%group Case,Gender,Number CGN
%%group Case,Gender,Number,lemma CGNL
%%group Person,Number PN
%%group Person,Number,Mood,lemma PNML
%%group lemma L
NP[CGNL=@] ::= NOUN[CGNL=@]
QP[CGNL=@] ::= NUM[CGNL=@]
QP[CGNL=@] ::= NUM[CGNL=@] ADP[L=de]
NP[CGNL=@] ::= QP[CGN=@] NP[CGNL=@]
 
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
parse('Doi de ani', parser)
p = parser.get_parses()[0][0]



