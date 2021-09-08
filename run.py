from dictionary import text_2_square_list
from cyk_parser import Parser, Grammar
from rule_io import rule_list_from_string

grammar_rules = """
NP[Case=@ Gender=@ Number=@] ::= NOUN[Case=@ Gender=@ Number=@]
AdjP[Case=@ Gender=@ Number=@] ::= ADJ[Case=@ Gender=@ Number=@]
NP[Case=@ Gender=@ Number=@] ::= NP[Case=@ Gender=@ Number=@] AdjP[Case=@ Gender=@ Number=@]
NP[Case=@ Gender=@ Number=@] ::= DetP[Case=@ Gender=@ Number=@] NP[Case=@ Gender=@ Number=@]
DetP[Case=@ Gender=@ Number=@] ::= DET[Case=@ Gender=@ Number=@]
VP[Number=@ Person=@] ::= NP[Number=@ Person=@] VERB[Number=@ Person=@]

"""

grammar = Grammar(rule_list_from_string(grammar_rules))
parser = Parser(grammar)
sq_list = text_2_square_list('Un băiat mergea')
table = parser.parse(sq_list)

