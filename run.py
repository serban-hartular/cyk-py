from dictionary import text_2_square_list, word_2_parse_square
from cyk.grammar import Grammar
import cyk.grammar_loader

from cyk.prob_parser import ProbabilisticParser
from cyk.piecewise_parser import PiecewiseParser

grammar_lines = []
# with open('./ro_locut.cfg', 'r', encoding='utf8') as fptr:
#     grammar_lines += fptr.readlines()
with open('rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
grammar = Grammar(cyk.grammar_loader.load_rules(grammar_lines))
    
# parser_old = Parser(grammar)
parser = PiecewiseParser(grammar)
def setup(text : str, _parser : ProbabilisticParser = parser):
    sq_list, unknown = text_2_square_list(text)
    if unknown:
        print('Unkown: ' + ', '.join(unknown))
    _parser.input(sq_list)



if __name__ == '__main__':
    setup('Sunt cunoscute astfel')
