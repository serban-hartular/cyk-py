from dictionary import text_2_square_list
from cyk_parser import Parser, Grammar
from cyk_grammar_loader import load_grammar

grammar_rules = """
%%group Case,Gender,Number CGN
%%group Case,Gender,Number,lemma CGNL
%%group Person,Number PN
%%group Person,Number,Mood,lemma PNML
%%group lemma L
NP[CGNL=@] ::= NOUN[CGNL=@]
AdjP[CGNL=@] ::= ADJ[CGNL=@]
DetP[CGNL=@] ::= DET[CGNL=@]
PP[L=@] ::= ADP[Case=@ L=@] NP[Case=@]
NP[CGNL=@] ::= DetP[CGN=@] NP[CGNL=@]
NP[CGNL=@] ::= NP[CGNL=@] AdjP[CGN=@]
NP[CGNL=@] ::= NP[CGNL=@] PP
VP[PNML=@] ::= NP[PN=@ Case=Nom] VERB[PNML=@]
VP[PNML=@] ::= VP[PNML=@] PP
VP[PNML=@] ::= VP[PNML=@] ADV
%reverse
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
parse('Un bou frumos mergea la mare', parser)
p = parser.get_parses()[0][0]



