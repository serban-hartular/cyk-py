from dictionary import text_2_square_list
from cyk_parser import Parser, Grammar
from cyk_grammar_loader import load_grammar

grammar_rules = """
NP[Case=@ Gender=@ Number=@] ::= NOUN[Case=@ Gender=@ Number=@]
AdjP[Case=@ Gender=@ Number=@] ::= ADJ[Case=@ Gender=@ Number=@]
NP[Case=@ Gender=@ Number=@] ::= NP[Case=@ Gender=@ Number=@] AdjP[Case=@ Gender=@ Number=@]
NP[Case=@ Gender=@ Number=@] ::= DetP[Case=@ Gender=@ Number=@] NP[Case=@ Gender=@ Number=@]
DetP[Case=@ Gender=@ Number=@] ::= DET[Case=@ Gender=@ Number=@]
VP[Number=@ Person=@] ::= NP[Number=@ Person=@] VERB[Number=@ Person=@]

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
parse('Un băiat mergea', parser)


